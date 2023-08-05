from osm_bot_abstraction_layer.generic_bot_retagging import run_simple_retagging_task


def edit_element_factory(editing_on_key, replacement_dictionary):
    def edit_element(tags):
        if tags.get(editing_on_key) in replacement_dictionary:
            tags[editing_on_key] = replacement_dictionary[tags[editing_on_key]]
            return tags
        return tags
    return edit_element

def fix_bad_values(editing_on_key, replacement_dictionary):
    edit_element_function = edit_element_factory(editing_on_key, replacement_dictionary)
    query = get_query(editing_on_key, replacement_dictionary)
    run_simple_retagging_task(
        max_count_of_elements_in_one_changeset=500,
        objects_to_consider_query=query,
        cache_folder_filepath='/media/mateusz/OSM_cache/osm_bot_cache',
        is_in_manual_mode=True,
        changeset_comment='fixing unusual ' + editing_on_key + ' values with a clear replacement',
        discussion_url=None,
        osm_wiki_documentation_page=None,
        edit_element_function=edit_element_function,
    )

def get_query(editing_on_key, replacement_dictionary):
    query = ""
    query += "[out:xml][timeout:1800];\n"
    query += "(\n"
    for from_value, to_value in replacement_dictionary.items():
        query += "  nwr['" + editing_on_key + "'='" + from_value + "'];\n"
    query += ");\n"
    query += "out body;\n"
    query += ">;\n"
    query += "out skel qt;\n"
    return query
