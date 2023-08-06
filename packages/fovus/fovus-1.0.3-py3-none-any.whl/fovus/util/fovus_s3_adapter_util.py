from fovus.util.aws_util import AwsUtil
from fovus.util.file_util import FileUtil
from fovus.util.util import Util

NUM_DECIMAL_POINTS_FILESIZE = 4


class FovusS3AdapterUtil:
    @staticmethod
    def print_pre_operation_information(operation, file_count, file_size_bytes, task_count):
        total_file_size_megabytes = round(Util.convert_bytes_to_megabytes(file_size_bytes), NUM_DECIMAL_POINTS_FILESIZE)
        total_file_size_gigabytes = round(Util.convert_bytes_to_gigabytes(file_size_bytes), NUM_DECIMAL_POINTS_FILESIZE)
        print(f"Beginning {operation}:")
        print(f"\tTask count:\t{task_count}")
        print(f"\tFile count:\t{file_count}")
        print(f"\tFile size:\t{total_file_size_megabytes} MB ({total_file_size_gigabytes} GB)")

    @staticmethod
    def print_post_operation_success(operation, is_success):
        operation_result = "Success!" if is_success else "Not successful."
        print(f"{operation_result} {operation} complete.")
        if operation == "Download":
            print(
                "Note: The download function operates as a sync. If a local file exists with the same path relative to "
                + "the job folder as a file in the cloud, and the two files are identical, it was not re-downloaded "
            )

    @staticmethod
    def should_download_file(local_filepath, s3_object):
        return not FileUtil.file_exists(local_filepath) or (
            FileUtil.get_file_hash(local_filepath) != AwsUtil.get_s3_object_hash(s3_object)
        )
