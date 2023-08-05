import boto3
import botocore
import json
import os
import io
import gzip
from gb_lib.GbLib import VolumeToWork

SESSION = boto3.Session()
S3 = SESSION.client('s3')


def gets3blob(s3Key):
    f = io.BytesIO()
    try:
        S3.download_fileobj('archive.tbrc.org', s3Key, f)
        return f
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == '404':
            return None
        else:
            raise


# This has a cache mechanism
def getImageList(s3_bucket: str, v_w: VolumeToWork) -> []:
    """
    Gets the image list as defined by a dimensions.json
    :param s3_bucket: source bucket
    :param v_w: Work and Volume
    :return:
    """

    # We don't have to worry about the image group name disjunction hack - these works are
    # already resolved in S3
    from archive_ops.shell_ws import get_mappings, Resolvers
    s3_work = get_mappings(s3_bucket + 'Works', v_w.work_name, Resolvers.S3_BUCKET)
    s3_key = f"{s3_work}/images/{v_w.work_name}-{v_w.volume_label}/dimensions.json"
    blob = gets3blob(s3_key)
    if blob is None:
        return None
    blob.seek(0)
    b = blob.read()
    ub = gzip.decompress(b)
    s = ub.decode('utf8')
    data = json.loads(s)
    return data


def iltogbinfo(imagelist):
    res = {}
    for i, imginfo in enumerate(imagelist):
        res["%08d" % (i + 1)] = imginfo["filename"]
    return res


def main():
    for i in range(423, 484):
        ig_label = f"W2PD17457-I4PD{i}"
        vw: VolumeToWork = VolumeToWork(ig_label)
        image_list = getImageList("ocr.bdrc.io", vw)
        gb_info = iltogbinfo(image_list)
        out_dir = f"info/{ig_label}"
        os.makedirs(out_dir, exist_ok=True)
        with open(out_dir + '/gb-bdrc-map.json', 'w', encoding='utf-8') as f:
            json.dump(gb_info, f, ensure_ascii=False)


main()
