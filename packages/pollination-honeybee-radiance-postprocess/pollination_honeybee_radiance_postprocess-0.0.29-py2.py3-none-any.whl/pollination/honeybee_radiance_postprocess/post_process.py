from dataclasses import dataclass
from pollination_dsl.function import Function, command, Inputs, Outputs


@dataclass
class AnnualDaylightMetrics(Function):
    """Calculate annual daylight metrics for annual daylight simulation."""

    folder = Inputs.folder(
        description='This folder is an output folder of annual daylight recipe. Folder '
        'should include grids_info.json and sun-up-hours.txt. The command uses the list '
        'in grids_info.json to find the result files for each sensor grid.',
        path='raw_results'
    )

    schedule = Inputs.file(
        description='Path to an annual schedule file. Values should be 0-1 separated '
        'by new line. If not provided an 8-5 annual schedule will be created.',
        path='schedule.txt', optional=True
    )

    thresholds = Inputs.str(
        description='A string to change the threshold for daylight autonomy and useful '
        'daylight illuminance. Valid keys are -t for daylight autonomy threshold, -lt '
        'for the lower threshold for useful daylight illuminance and -ut for the upper '
        'threshold. The default is -t 300 -lt 100 -ut 3000. The order of the keys is not'
        ' important and you can include one or all of them. For instance if you only '
        'want to change the upper threshold to 2000 lux you should use -ut 2000 as '
        'the input.', default='-t 300 -lt 100 -ut 3000'
    )

    @command
    def calculate_annual_metrics(self):
        return 'honeybee-radiance-postprocess post-process annual-daylight ' \
            'raw_results --schedule schedule.txt {{self.thresholds}} ' \
            '--sub-folder metrics'

    # outputs
    annual_metrics = Outputs.folder(
        description='Annual metrics folder. This folder includes all the other '
        'sub-folders which are also exposed as separate outputs.', path='metrics'
    )

    daylight_autonomy = Outputs.folder(
        description='Daylight autonomy results.', path='metrics/da'
    )

    continuous_daylight_autonomy = Outputs.folder(
        description='Continuous daylight autonomy results.', path='metrics/cda'
    )

    useful_daylight_illuminance_lower = Outputs.folder(
        description='Lower useful daylight illuminance results.',
        path='metrics/udi_lower'
    )

    useful_daylight_illuminance = Outputs.folder(
        description='Useful daylight illuminance results.', path='metrics/udi'
    )

    useful_daylight_illuminance_upper = Outputs.folder(
        description='Upper useful daylight illuminance results.',
        path='metrics/udi_upper'
    )


@dataclass
class AnnualDaylightEN17037Metrics(Function):
    """Calculate annual daylight EN 173037 metrics for annual daylight simulation."""

    folder = Inputs.folder(
        description='This folder is an output folder of annual daylight recipe. Folder '
        'should include grids_info.json and sun-up-hours.txt. The command uses the list '
        'in grids_info.json to find the result files for each sensor grid.',
        path='raw_results'
    )

    schedule = Inputs.file(
        description='Path to an annual schedule file. Values should be 0-1 separated '
        'by new line. This should be a daylight hours schedule according to EN 17037.',
        path='schedule.txt'
    )

    @command
    def calculate_annual_metrics_en17037(self):
        return 'honeybee-radiance-postprocess post-process annual-daylight-en17037 ' \
            'raw_results schedule.txt --sub_folder metrics'

    # outputs
    annual_en17037_metrics = Outputs.folder(
        description='Annual EN 17037 metrics folder. This folder includes all the other '
        'subfolders which are also exposed as separate outputs.', path='metrics'
    )

    daylight_autonomy = Outputs.folder(
        description='Daylight autonomy results.', path='metrics/da'
    )

    spatial_daylight_autonomy = Outputs.folder(
        description='Spatial daylight autonomy results.', path='metrics/sda'
    )
