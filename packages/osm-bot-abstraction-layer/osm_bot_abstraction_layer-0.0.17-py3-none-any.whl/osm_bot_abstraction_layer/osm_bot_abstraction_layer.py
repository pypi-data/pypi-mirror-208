# docs: http://osmapi.metaodi.ch/
import osmapi
import time
import json

def fully_automated_description():
    return "yes"

def manually_reviewed_description():
    return "no, it is a manually reviewed edit"

def get_api(account_type):
    with open('secret.json') as f:
        data = json.load(f)
        username = data[account_type]['username']
        password = data[account_type]['password']
        return osmapi.OsmApi(username = username, password = password)

def character_limit_of_description():
    return 255
 
class ChangesetBuilder:
    def __init__(self, affected_objects_description, comment, automatic_status, discussion_url, osm_wiki_documentation_page, source, other_tags_dict = {}):
        self.changeset_description = other_tags_dict
        self.changeset_description['automatic'] = automatic_status
        if automatic_status == fully_automated_description():
            if osm_wiki_documentation_page == None or discussion_url == None:
                raise "missing links to the automatic edit documentation!"
            self.changeset_description['bot'] = 'yes' # recommended on https://wiki.openstreetmap.org/wiki/Automated_Edits_code_of_conduct
            self.changeset_description["discussion_before_edits"] = discussion_url
            self.changeset_description["osm_wiki_documentation_page"] = osm_wiki_documentation_page
        self.changeset_description['created_by_library'] = "https://github.com/matkoniecz/osm_bot_abstraction_layer"
        self.changeset_description['cases_where_human_help_is_required'] = 'https://matkoniecz.github.io/OSM-wikipedia-tag-validator-reports/'
        if source != None:
            self.changeset_description["source"] = source
        self.changeset_description['comment'] = output_full_comment_get_comment_within_limit(affected_objects_description, comment)

    def create_changeset(self, api):
        print("opening changeset", json.dumps(self.changeset_description, sort_keys=True, indent=4))
        try:
            api.ChangesetCreate(self.changeset_description)
        except osmapi.OsmApi.ApiError as e:
            print(e.payload)
            print(e.reason)
            print(e.status_code)
            raise

def get_data(id, type):
    print("downloading https://www.openstreetmap.org/" + type + "/" + str(id))
    api = get_api('bot_account')
    try:
        if type == 'node':
            return api.NodeGet(id)
        if type == 'way':
            return api.WayGet(id)
        if type == 'relation':
            return api.RelationGet(id)
        if type == 'note':
            return api.NoteGet(id)
    except osmapi.ElementDeletedApiError:
        return None
    assert(False)

def get_notes_in_area(min_lon, min_lat, max_lon, max_lat, limit=10_000, number_of_days_before_closed_note_is_hidden=0):
    # https://osmapi.metaodi.ch/osmapi/OsmApi.html#OsmApi.NotesGet
    # https://wiki.openstreetmap.org/wiki/API_v0.6#Retrieving_notes_data_by_bounding_box:_GET_/api/0.6/notes
    # number_of_days_before_closed_note_is_hidden:
    # A value of 0 means only open notes are returned. A value of -1 means all notes are returned. 
    if limit < 1 or limit > 10_000:
        raise Exception("A value of between 1 and 10000 is valid")
    api = get_api('bot_account')
    # https://osmapi.metaodi.ch/osmapi/OsmApi.html#OsmApi.NotesGet
    #print("NotesGet(min_lon " + str(min_lon) + " min_lat: " + str(min_lat) + " max_lon: " +  str(max_lon) + " max_lat: " + str(max_lat) + " limit" + str(limit) + " number_of_days_before_closed_note_is_hidden: " + str(number_of_days_before_closed_note_is_hidden) + ")")
    #print("import osmapi")
    #print("NotesGet(" + str(min_lon) + ", " + str(min_lat) + ", " +  str(max_lon) + ", " + str(max_lat) + ", limit=" + str(limit) + ", closed=" + str(number_of_days_before_closed_note_is_hidden) + ")")
    uri = (
            "https://api.openstreetmap.org/api/0.6/notes?bbox=%f,%f,%f,%f&limit=%d&closed=%d"
            % (min_lon, min_lat, max_lon, max_lat, limit, number_of_days_before_closed_note_is_hidden)
        )
    #print(uri)
    try:
        return api.NotesGet(min_lon, min_lat, max_lon, max_lat, limit=limit, closed=number_of_days_before_closed_note_is_hidden)
    except osmapi.XmlResponseInvalidError:
        # https://github.com/metaodi/osmapi/issues/137
        return []

def close_note(noteId, comment, api_code):
    api = get_api(api_code)
    api.NoteClose(noteId, comment)

def update_element(api, type, data):
    """
    Updates object with the supplied data dict.

    For nodes:
        #!python
        {
            'id': id of node,
            'lat': latitude of node,
            'lon': longitude of node,
            'tag': {},
            'version': version number of node,
        }

    https://github.com/metaodi/osmapi/blob/master/osmapi/OsmApi.py#L308
    https://github.com/metaodi/osmapi/blob/dccb636e1e07b56c936a454997bc2763fb1d8031/osmapi/OsmApi.py#L308

    For ways?:

    For relations?:
    """

    try:
        if type == 'node':
            return api.NodeUpdate(data)
        if type == 'way':
            return api.WayUpdate(data)
        if type == 'relation':
            return api.RelationUpdate(data)
        assert False, str(type) + " type as not recognised"
    except osmapi.ApiError as e:
        print(e)
        raise e

def delete_element(api, type, data):
    try:
        if type == 'node':
            return api.NodeDelete(data)
        if type == 'way':
            return api.WayDelete(data)
        if type == 'relation':
            return api.RelationDelete(data)
        assert False, str(type) + " type as not recognised"
    except osmapi.ApiError as e:
        print(e)
        raise e

def sleep(time_in_s):
    print("Sleeping")
    time.sleep(time_in_s)

def get_correct_api(automatic_status, discussion_url, osm_wiki_documentation_page):
    if automatic_status == manually_reviewed_description():
        return get_api('human_account')
    elif automatic_status == fully_automated_description():
        if discussion_url == None:
            raise Exception("bot edits must be discussed before edit")
        if osm_wiki_documentation_page == None:
            raise Exception("bot edits must be documented before edit")
        return get_api('bot_account')
    else:
        assert(False)

def output_full_comment_get_comment_within_limit(affected_objects_description, comment):
    full_comment = affected_objects_description + " " + comment
    if(len(comment) > character_limit_of_description()):
        raise "comment too long"
    if(len(full_comment) <= character_limit_of_description()):
        comment = full_comment
    print(full_comment)
    return comment

def make_edit(affected_objects_description, comment, automatic_status, discussion_url, osm_wiki_documentation_page, element_type, data, source, sleeping_time=60, other_changeset_tags_dict={}):
    api = get_correct_api(automatic_status, discussion_url, osm_wiki_documentation_page)
    builder = ChangesetBuilder(affected_objects_description, comment, automatic_status, discussion_url, osm_wiki_documentation_page, source, other_changeset_tags_dict)
    builder.create_changeset(api)
    update_element(api, element_type, data)
    api.ChangesetClose()
    if sleeping_time != 0:
        sleep(sleeping_time)

def get_and_verify_data(osm_object_url, prerequisites, prerequisite_failure_callback=None):
    element_type = osm_object_url.split("/")[3]
    id = osm_object_url.split("/")[4]
    data = get_data(id, element_type)
    if data == None:
        return None
    failure = prerequisite_failure_reason(osm_object_url, prerequisites, data, prerequisite_failure_callback)
    if failure != None:
        print(failure)
        return None
    return data

def prerequisite_failure_reason(osm_object_url, prerequisites, data, prerequisite_failure_callback=None):
    if prerequisite_failure_callback != None:
        failure_reason = prerequisite_failure_callback(data)
        if failure_reason != None:
            return osm_object_url + " failed with " + failure_reason

    for key in prerequisites.keys():
        if prerequisites[key] == None:
            if key in data['tag']:
                return("failed " + key + " prerequisite, as key " + key + " was present for " + osm_object_url)
        elif key not in data['tag']:
            return("failed " + key + " prerequisite, as key " + key + " was missing for " + osm_object_url)
        elif prerequisites[key] != data['tag'][key]:
            return("failed " + key + " prerequisite for " + osm_object_url)
    return None

def get_all_nodes_of_an_object(osm_object_url):
    element_type = osm_object_url.split("/")[3]
    id = osm_object_url.split("/")[4]
    object_data = get_data(id, element_type)
    if element_type != "way" and element_type != "node" and element_type != "relation":
        error = "unexpected type " + str(element_type)
        print(error)
        raise ValueError(error)
    if element_type == "relation":
        for member in object_data["member"]:
            if member['type'] == 'way':
                way_url = "https://www.openstreetmap.org/way/" + str(member['ref'])
                way_data = get_data(member['ref'], 'way')
                print("recursive calling from " + osm_object_url + " to " + way_url)
                #pprint.pprint(data)
                for entry in get_all_nodes_of_an_object(way_url):
                    yield entry
            elif member['type'] == 'node':
                yield member['ref']
            elif member['type'] == 'relation':
                error = "for now not all relations are supported (handling cycles would be necessary)"
                print(error)
                for node in get_all_nodes_of_an_object("https://www.openstreetmap.org/relation/" + str(member['ref'])):
                    yield node
            #pprint.pprint(member['type'])
            #pprint.pprint(member['ref'])
    if element_type == "node":
        print(object_data)
        yield object_data["id"]
    if element_type == "way":
        for entry in object_data["nd"]:
            yield entry
