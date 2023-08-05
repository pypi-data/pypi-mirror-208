from dataclasses import dataclass
from pollination_dsl.function import Function, command, Inputs, Outputs


@dataclass
class MergeFolderData(Function):
    """Restructure files in a distributed folder."""

    input_folder = Inputs.folder(
        description='Input sensor grids folder.',
        path='input_folder'
    )

    extension = Inputs.str(
        description='Extension of the files to collect data from. It will be ``pts`` '
        'for sensor files. Another common extension is ``ill`` for the results of '
        'daylight studies.'
    )

    dist_info = Inputs.file(
        description='Distribution information file.',
        path='dist_info.json', optional=True
    )

    @command
    def merge_files_in_folder(self):
        return 'honeybee-radiance-postprocess grid merge-folder ./input_folder ' \
            './output_folder {{self.extension}} --dist-info dist_info.json'

    output_folder = Outputs.folder(
        description='Output folder with newly generated files.', path='output_folder'
    )
