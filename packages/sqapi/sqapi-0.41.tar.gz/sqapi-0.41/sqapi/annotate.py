import inspect
import json

import time
import traceback

from sqapi.request import Get
from sqapi.api import SQAPI, DEFAULT_HOST
from sqapi.media import SQMediaObject

DEFAULT_PROB_THRESH = 0.5
DEFAULT_POLL_DELAY = 5
DEFAULT_ANNOTATOR_NAME = '{user[first_name]}-{user[last_name]}'


class Annotator:
    def __init__(self, host: str = DEFAULT_HOST, api_key: str = None, annotator_info: str = None,
                 prob_thresh: float = DEFAULT_PROB_THRESH, poll_delay: int = DEFAULT_POLL_DELAY,
                 label_map_file: str = None, verbosity: int = 2, email_results: bool = None, **kw):
        """
        Generic annotator abstract class

        :param annotator_info: used for the name of the annotation_set, include version info, defaults to ClassName
        :param label_map_file: path to a local file that contains the label mappings
        :param prob_thresh: probability threshold for submitted labels, only submitted if p > prob_thresh
        :param poll_delay: the poll delay for running the loop. To run once, set poll_delay = -1
        :param annotation_set_id: if supplied, will create suggested labels to the specific annotation_set with that ID
        :param affiliation_group_id: if supplied, will attempt to annotate all annotation_sets within an affiliation group
        :param user_group_id: if supplied, will attempt to annotate all annotation_sets within a user_group
        :param after_date: filter annotation_sets that were created after a specific date
        :param host: the Squidle+ instance hostname
        :param api_key: the API key for the user on that `host`. If omitted, you'll be asked to log in.
        :param verbosity: the verbosity of the output (0,1,2,3)
        :param email_results: flag to optionally send an email upon completion
        """
        annotator_info = annotator_info or self.__class__.__name__
        self.sqapi = SQAPI(host=host, api_key=api_key, verbosity=verbosity)
        self.annotator_info = annotator_info.format(user=self.sqapi.current_user)  #(annotator_name or self.sqapi.cliargs.annotator_name).format(user=self.sqapi.current_user)
        self.prob_thresh = prob_thresh #or self.sqapi.cliargs.prob_thresh
        self.poll_delay = poll_delay #or self.sqapi.cliargs.poll_delay
        self.label_map_file = label_map_file #or self.sqapi.cliargs.label_map_file
        self.email_results = email_results
        self.labels = []
        self.label2id = None

    def start(self, annotation_set_request: Get):
        """

        :param annotation_set_request:
        :return:
        """
        while True:
            self.run(annotation_set_request)
            if isinstance(self.poll_delay, (float, int)) and self.poll_delay > 0:
                time.sleep(self.poll_delay)
            else:
                break

    def run(self, annotation_set_request: Get, page=1, results_per_page=200, email_results=None):
        """

        :param annotation_set_request:
        :param page:
        :param results_per_page:
        :param email_results:
        :return:
        """
        annotation_sets = annotation_set_request.page(page).results_per_page(results_per_page).execute().json()

        print(f"\nFOUND: {annotation_sets.get('num_results')} annotation_sets | processing page {annotation_sets.get('page')}/{annotation_sets.get('total_pages')}...\n")

        # process current page of annotation_sets
        i = 0
        for a in annotation_sets.get("objects"):
            try:
                i += 1
                print(f"{'*'*80}\nProcessing ANNOTATION_SET: {(annotation_sets.get('page')-1)*results_per_page+i} / {annotation_sets.get('num_results')} | ID:{a.get('id')} > {a.get('name')} [{a.get('user',{}).get('username')}] ...\n{'*'*80}\n")
                media_count, point_count, annotation_count = self.process_annotation_set(a)
                if self.email_results if email_results is None else email_results:
                    self.email_annotation_set_user(a, media_count, point_count, annotation_count)
            except Exception as e:
                print(traceback.format_exc())

        # paginate annotation_sets, if more than one page returned
        if annotation_sets.get("page") < annotation_sets.get("total_pages"):
            self.run(annotation_set_request=annotation_set_request, page=page+1, results_per_page=results_per_page, email_results=email_results)

    def process_annotation_set(self, annotation_set_data):
        """

        :param annotation_set_data:
        :return:
        """
        code2label = self.get_label_mappings(annotation_set_data)
        new_annotation_set = self.create_supplemental_annotation_set(parent_data=annotation_set_data)
        media_count, point_count, annotation_count = self.annotate_media_list(new_annotation_set, code2label=code2label)
        return media_count, point_count, annotation_count

    def get_label_mappings(self, annotatation_set_data):
        """

        :param annotatation_set_data:
        :return:
        """
        label_scheme_id = annotatation_set_data.get("label_scheme", {}).get("id")
        label_scheme_data = self.sqapi.get(f"/api/label_scheme/{label_scheme_id}").execute().json()
        parent_label_scheme_ids = label_scheme_data.get("parent_label_scheme_ids")
        with open(self.label_map_file) as f:
            label_map_filters = json.load(f)
        if isinstance(label_map_filters, dict):
            code2label = {}
            for l, filts in label_map_filters.items():
                code2label[l] = self.get_label(filts, parent_label_scheme_ids)
        elif isinstance(label_map_filters, list):
            code2label = []
            for filts in label_map_filters:
                code2label.append(self.get_label(filts, parent_label_scheme_ids))
        else:
            raise TypeError("Unknown `label_map_filters` type. Must be a `list` or a `dict`")

        return code2label

    def get_label(self, filts, label_scheme_ids:list):
        """

        :param filts:
        :param label_scheme_ids:
        :return:
        """
        if isinstance(filts, list):
            r = self.sqapi.get("/api/label", single=True).filters_and(filts)
            r.filter(name="label_scheme_id", op="in", val=label_scheme_ids)
            return r.execute().json()
        return None

    def create_supplemental_annotation_set(self, parent_data, child_name=None, child_description=None):
        """

        :param parent_data:
        :param child_name:
        :param child_description:
        :return:
        """
        child_data = dict()
        child_data["user_id"] = self.sqapi.current_user.get("id")
        child_data['media_collection_id'] = parent_data.get("media_collection",{}).get("id")
        child_data['label_scheme_id'] = parent_data.get('label_scheme',{}).get('id')
        child_data['parent_id'] = parent_data.get('id')
        child_data['description'] = child_description or "Suggested annotations by '{}' for the '{}' annotation_set." \
                              "This is not a standalone annotation set.".format(self.annotator_info, parent_data.get("name"))
        child_data['name'] = child_name or self.annotator_info

        return self.sqapi.post("/api/annotation_set", json_data=child_data).execute().json()

    def annotate_media_list(self, annotation_set_data, code2label=None, page=1, results_per_page=500):
        """

        :param annotation_set_data:
        :param code2label:
        :param page:
        :param results_per_page:
        :return:
        """
        annotation_set_id = annotation_set_data.get("id")
        media_collection_id = annotation_set_data.get("media_collection",{}).get("id")
        # media_list =self.get_media_collection_media(media_collection_id, page=page, results_per_page=results_per_page)
        media_list = self.sqapi.get("/api/media", page=page, results_per_page=results_per_page).filter(
            name="media_collections", op="any", val=dict(name="id", op="eq", val=media_collection_id)
        ).order_by(field="timestamp_start", direction="asc").execute().json()
        num_results = media_list.get('num_results')
        media_count = point_count = annotation_count = 0

        for m in media_list.get("objects"):
            media_count += 1
            print(f"\nProcessing: media item {media_count + (page-1)*results_per_page} / {num_results}")
            media_url = m.get('path_best')
            media_type = m.get("media_type", {}).get("name")
            mediaobj = SQMediaObject(media_url, media_type=media_type, media_id=m.get('id'))

            # get media annotations. If this frame has not been observed, it will generat the annotations through the request
            base_annotation_set_id = annotation_set_data.get("parent_id") or annotation_set_data.get("id")
            media_annotations = self.sqapi.get(f"/api/media/{m.get('id')}/annotations/{base_annotation_set_id}").execute().json()
            points = media_annotations.get('annotations')
            point_count += len(points)

            # run point predictions
            annotations = []
            for p in points:
                point_id = p.get("id")
                x = p.get('x')
                y = p.get('y')
                t = p.get('t')

                # decide whether a point label or a frame label
                if x is not None and y is not None:
                    code, probability = self.classify_point(mediaobj, x=x, y=y, t=t)
                else:
                    code, probability = self.classify_frame(mediaobj, t=t)

                # print(f"code: {code}, prob: {probability}")
                # time.sleep(1)

                # lookup label_id from classifier code. If dict, use get, otherwise assume list index code
                if code is not None:
                    label = code2label[code]   # if dict, use key, otherwise treat as index to list

                    # build up annotations list
                    if label is not None:
                        annotations.append(dict(
                            user_id=self.sqapi.current_user.get("id"),
                            label_id=label.get("id"),
                            annotation_set_id=annotation_set_id,
                            point_id=point_id,
                            likelihood=float(probability)
                            # data=dict(probability=float(probability))
                        ))

            # Submit and save any new annotations
            for a in annotations:
                if a.get('likelihood', 0) >= self.prob_thresh:
                    self.sqapi.post("/api/annotation", json_data=a).execute()
                    annotation_count += 1

        # continue until all images are processed
        if media_list.get("page") < media_list.get("total_pages"):
            _mc, _pc, _ac = self.annotate_media_list(
                annotation_set_data, code2label=code2label, page=page+1, results_per_page=results_per_page)
            media_count += _mc
            point_count += _pc
            annotation_count += _ac

        return media_count, point_count, annotation_count

    def email_annotation_set_user(self, a, media_count, point_count, annotation_count):
        user_ids = [a.get('user', {}).get('id')]
        annotation_set_url = "{}/geodata/annotation_set/{}".format(self.sqapi.host, a.get("id"))
        message = f'Hi {a.get("user",{}).get("first_name")}, <br><br>\n' \
                  f'Your annotation set "{a.get("media_collection",{}).get("name")} >> {a.get("name")}" has new ' \
                  f'suggested annotations!<br>\n' \
                  f'{self.annotator_info} processed: {media_count} media items with {point_count} points and ' \
                  f'submitted {annotation_count} annotations which will appear as "Magical Suggestions".<br><br>\n' \
                  f'To see results, click: <a href="{annotation_set_url}">{annotation_set_url}</a>'
        self.sqapi.send_user_email("SQ+ BOT: your Annotation Set has been processed", message, user_ids=user_ids)

    def classify_point(self, mediaobj: SQMediaObject, x, y, t):
        """

        :param mediaobj:
        :param x:
        :param y:
        :param t:
        :return:
        """
        print(f"media_url: {mediaobj.url}\nx: {x}\ny: {y}\nt: {t}")
        return None, 0.0

    def classify_frame(self, mediaobj: SQMediaObject, t):
        """

        :param mediaobj:
        :param t:
        :return:
        """
        print(f"media_url: {mediaobj.url}\nt: {t}")
        return None, 0.0

    def detect_points(self, mediaobj: SQMediaObject):
        """

        :param mediaobj:
        :return:
        """
        return []





