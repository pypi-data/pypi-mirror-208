"""Handlers for daylight simulation."""
import os
import json

from ladybug.datacollection import HourlyContinuousCollection
from .helper import read_sensor_grid_result, read_grid_results


def read_df_from_folder(result_folder):
    """Read daylight factor values from a folder with radiance .res result files."""
    return read_sensor_grid_result(result_folder, 'res', 'full_id')


def read_pit_from_folder(result_folder):
    """Read point-in-time results from a folder with radiance .res result files."""
    return read_sensor_grid_result(result_folder, 'res', 'full_id', False)


def read_da_from_folder(result_folder):
    """Read daylight autonomy values from a folder with radiance .da result files."""
    return read_sensor_grid_result(result_folder, 'da', 'full_id')


def read_cda_from_folder(result_folder):
    """Read continuous daylight autonomy values from a folder with .cda result files."""
    return read_sensor_grid_result(result_folder, 'cda', 'full_id')


def read_udi_from_folder(result_folder):
    """Read useful daylight illuminance from a folder with radiance .udi result files."""
    return read_sensor_grid_result(result_folder, 'udi', 'full_id')


def read_ga_from_folder(result_folder):
    """Read glare autonomy values from a folder with radiance .da result files."""
    return read_sensor_grid_result(result_folder, 'ga', 'full_id')


def read_hours_from_folder(result_folder):
    """Read hours from a folder with radiance .res result files."""
    return read_sensor_grid_result(result_folder, 'res', 'full_id', False)


def read_ase_from_folder(result_folder):
    """Read annual sunlight exposure values from a folder with radiance .ase result files."""
    return read_grid_results(result_folder, 'ase', 'full_id')


def sort_ill_from_folder(result_folder):
    """Sort the .ill files from an annual study so that they align with Model grids.
    """
    # check that the required files are present
    if not os.path.isdir(result_folder):
        raise ValueError('Invalid result folder: %s' % result_folder)
    grid_json = os.path.join(result_folder, 'grids_info.json')
    if not os.path.isfile(grid_json):
        raise ValueError('Result folder contains no grids_info.json.')

    # load the list of grids and gather all of the result files
    with open(grid_json) as json_file:
        grid_list = json.load(json_file)
    results = []
    for grid in grid_list:
        try:
            id_ = grid['full_id']
        except KeyError:
            # older version
            id_ = grid['identifier']
        result_file = os.path.join(result_folder, '{}.ill'.format(id_))
        if os.path.isfile(result_file):
            results.append(result_file)
    sun_up_file = os.path.join(result_folder, 'sun-up-hours.txt')
    if os.path.isfile(sun_up_file):
        results.append(sun_up_file)
    return results


def read_images_from_folder(result_folder):
    """Read hdr images from a folder in a manner that aligns with Model views."""
    # check that the required files are present
    if not os.path.isdir(result_folder):
        raise ValueError('Invalid result folder: %s' % result_folder)
    view_json = os.path.join(result_folder, 'views_info.json')
    if not os.path.isfile(view_json):
        raise ValueError('Result folder contains no views_info.json.')

    # load the list of views and gather all of the result files
    with open(view_json) as json_file:
        view_list = json.load(json_file)
    results = []
    for view in view_list:
        id_ = view['full_id']
        result_file = os.path.join(result_folder, '{}.HDR'.format(id_))
        if os.path.isfile(result_file):
            results.append(result_file)
    return results


def ill_credit_json_from_path(eui_json):
    """Read the credit summary values from the credit_summary.json file."""
    if not os.path.isfile(eui_json):
        raise ValueError('Invalid file path: %s' % eui_json)
    with open(eui_json) as json_file:
        data = json.load(json_file)
    results = []
    for key in sorted(data.keys()):
        results.append('{}: {}'.format(key, data[key]))
    return results


def read_leed_datacollection_from_folder(result_folder):
    """Read LEED Daylight Option I datacollections """
    # check that the required files are present
    if not os.path.isdir(result_folder):
        raise ValueError('Invalid result folder: %s' % result_folder)
    grid_json = os.path.join(result_folder, 'grids_info.json')
    if not os.path.isfile(grid_json):
        raise ValueError('Result folder contains no grids_info.json.')

    # load the list of grids and gather all of the results
    with open(grid_json) as json_file:
        grid_list = json.load(json_file)
    results = []
    for grid in grid_list:
        grid_id = grid['full_id']
        result_file = os.path.join(result_folder, '{}.{}'.format(grid_id, 'json'))
        with open(result_file) as json_file:
            data = json.load(json_file)
            datacollection = HourlyContinuousCollection.from_dict(data)
            results.append(datacollection)

    return results


def read_leed_shade_transmittance_schedule(shd_json):
    """Read LEED Daylight Option I shade transmittance schedule."""
    if not os.path.isfile(shd_json):
        raise ValueError('Invalid file path: %s' % shd_json)
    results = []
    with open(shd_json) as json_file:
        data = json.load(json_file)
        for data_dict in data.values():
            datacollection = HourlyContinuousCollection.from_dict(data_dict)
            results.append(datacollection)

    return results
