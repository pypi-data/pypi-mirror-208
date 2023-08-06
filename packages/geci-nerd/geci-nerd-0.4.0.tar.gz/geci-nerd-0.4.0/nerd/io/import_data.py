from nerd.io.geo2utm import geo2utm
from nerd.calibration.fit_flow_rate import fit_flow_rate
import nerd.density_functions
import pandas as pd
import os

column_names = ["date", "time", "Lat", "Lon", "Speed", "heading", "Logging_on", "altitude"]
flux_calibation_colums = ["aperture_diameter", "flux"]


def tracmap2csv(tracmap_filename, csv_filename):
    tracmap_data = pd.read_csv(
        tracmap_filename, header=None, names=column_names, usecols=[i for i in range(1, 9)]
    )
    tracmap_data.to_csv(csv_filename, index=False)


def import_tracmap(tracmap_filename, csv_filename="input_data.csv"):
    tracmap2csv(tracmap_filename, csv_filename)
    return geo2utm(csv_filename)


def import_calibration_data(flux_filename):
    flux_data = pd.read_csv(
        flux_filename,
        header=None,
        skiprows=1,
        names=flux_calibation_colums,
        usecols=[i for i in range(0, 2)],
    )
    return fit_flow_rate(flux_data["aperture_diameter"].to_numpy(), flux_data["flux"].to_numpy())


def check_output_directory(output_path):
    if not os.path.exists(output_path):
        os.mkdir(output_path)


def import_multifile_tracmap(config_file, csv_filename):
    df_list = create_df_list(config_file)
    df_concat = pd.concat(df_list)
    output_path = config_file.get("output_path")
    check_output_directory(output_path)
    concatenated_tracmap_path = "{}/{}".format(output_path, csv_filename)
    df_concat.to_csv(concatenated_tracmap_path, index=False)
    return geo2utm(concatenated_tracmap_path)


def create_df_list(config_file):
    df_list = [
        pd.read_csv(
            resources["input_data_path"],
            header=None,
            names=column_names,
            usecols=[i for i in range(1, 9)],
        )
        for resources in config_file["resources"]
    ]
    return df_list


def select_parameters_by_index(config_file, n_file):
    aperture_diameter = config_file["resources"][n_file]["aperture_diameter"]
    swap_width = config_file["resources"][n_file]["swap_width"]
    density_function = select_density_function(config_file["resources"][n_file]["density_function"])
    return aperture_diameter, swap_width, density_function


def select_density_function(function_name):
    return getattr(nerd.density_functions, function_name)
