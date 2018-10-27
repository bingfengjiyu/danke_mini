# coding:utf-8
from werkzeug.utils import secure_filename
from flask import current_app, render_template, jsonify, request, make_response, send_from_directory
import os
from danke.libs import strUtil
from . import api
from danke import constants


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in constants.ALLOWED_EXTENSIONS


basedir = os.path.abspath(os.path.dirname(__file__))


# 上传文件
# @api.route('/up_photo', methods=['POST'], strict_slashes=False)
def api_upload():
    file_dir = os.path.join(basedir, current_app.config['UPLOAD_FOLDER'])
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    f = request.files['photo']
    if f and allowed_file(f.filename):
        fname = secure_filename(f.filename)
        print(fname)
        try:
            ext = fname.rsplit('.', 1)[1]
            new_filename = strUtil.Pic_str().create_uuid() + '.' + ext
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(code=201, msg="非法操作")

        f.save(os.path.join(file_dir, new_filename))
        print(file_dir+new_filename)
        return file_dir+new_filename
    else:
        return False


@api.route('/download/<string:filename>', methods=['GET'])
def download(filename):
    if request.method == "GET":
        if os.path.isfile(os.path.join('upload', filename)):
            return send_from_directory('upload', filename, as_attachment=True)
        pass


# show photo
@api.route('/show/<string:filename>', methods=['GET'])
def show_photo(filename):
    file_dir = os.path.join(basedir, current_app.config['UPLOAD_FOLDER'])
    if request.method == 'GET':
        if filename is None:
            pass
        else:
            image_data = open(os.path.join(file_dir, '%s' % filename), "rb").read()
            response = make_response(image_data)
            response.headers['Content-Type'] = 'image/png'
            return response
    else:
        pass




