import logging
import os
import shutil
import subprocess
import sys
from abc import ABC
from urllib.parse import unquote
from uuid import uuid4

from redis import Redis
from rq import Queue
from rq.job import Job
from tornado import gen, iostream
from tornado.escape import json_decode

import settings
from tornado.web import RequestHandler, stream_request_body

from diannpy.operation import Diann

r = Redis(os.getenv("REDIS_HOST"))
q = Queue(connection=r)

class BaseHandler(RequestHandler, ABC):
    def set_default_headers(self):
        self.set_header("access-control-allow-origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'GET, PUT, DELETE, OPTIONS')
        self.set_header("Access-Control-Allow-Headers", "access-control-allow-origin,authorization,content-type,unique-id,filename")

    def options(self, **kwargs):
        self.set_status(204)
        self.finish()


class MainHandler(BaseHandler, ABC):
    def get(self):
        self.write(str(uuid4()))


@stream_request_body
class UploadHandler(BaseHandler):
    def initialize(self):
        self.byte_read = 0

    @gen.coroutine
    def data_received(self, chunk):
        if "open_file" not in self.__dict__:
            uniqueID = self.request.headers.get("Unique-ID")
            self.filename = self.request.headers.get("Filename")
            self.folder_path = os.path.join(settings.location, uniqueID)
            os.makedirs(self.folder_path, exist_ok=True)
            os.makedirs(os.path.join(self.folder_path, "temp"), exist_ok=True)
            os.makedirs(os.path.join(self.folder_path, "data"), exist_ok=True)
            self.path = os.path.join(self.folder_path, "temp", self.filename)
            self.open_file = open(self.path, "wb")
        self.open_file.write(chunk)
        self.byte_read += len(chunk)

    def put(self):
        #mtype = self.request.headers.get("Content-Type")
        #logging.info('PUT "%s" "%s" %d bytes', filename, mtype, self.bytes_read)
        self.open_file.close()
        if sys.platform.startswith("win32"):
            with open(self.path, "rt") as tempfile, \
                    open(os.path.join(self.folder_path, "data", self.filename), "wt", newline="") as datafile:
                boundary_pass = False
                for line in tempfile:
                    templine = line.strip()
                    if templine.startswith("------WebKitFormBoundary"):
                        if boundary_pass == True:
                            break
                        continue
                    elif templine.startswith("Content-"):
                        continue
                    elif templine == "" and boundary_pass == False:
                        boundary_pass = True
                        continue
                    else:
                        datafile.write(line)
        else:
            p1 = subprocess.Popen(["tail", "-n", "+5", self.path], stdout=subprocess.PIPE)
            with open(os.path.join(self.folder_path, "data", self.filename), "wb") as datafile:
                subprocess.run(["head", "-n", "-2"], stdin=p1.stdout, stdout=datafile)

        self.write("OK")


def run_diann(folder_path, uniqueID, fasta, gaf, obo):
    os.makedirs(os.path.join(folder_path, "DIANN"), exist_ok=True)
    if fasta != "":
        fasta = os.path.join(folder_path, "data", fasta)
    if gaf != "":
        gaf = os.path.join(folder_path, "data", gaf)
    if obo != "":
        obo = os.path.join(folder_path, "data", obo)
    with Diann(os.path.join(folder_path, "data"), os.path.join(folder_path, "DIANN"), fasta, gaf, obo) as diann:
        print("diann")
    shutil.make_archive(os.path.join(folder_path, uniqueID), "zip", os.path.join(folder_path, "DIANN"))


class DiannHandler(BaseHandler, ABC):
    @gen.coroutine
    def get(self, uniqueID, fasta, gaf, obo):
        folder_path = os.path.join(settings.location, uniqueID)
        result = q.enqueue(run_diann, args=(folder_path, uniqueID, fasta, gaf, obo), job_timeout="2h",  job_id=uniqueID)
        self.write(result.id)

    @gen.coroutine
    def post(self):
        req = json_decode(self.request.body)
        folder_path = os.path.join(settings.location, req["uniqueID"])
        result = q.enqueue(run_diann, args=(folder_path, req["uniqueID"], req["fasta"], req["gaf"], req["obo"]), job_timeout="2h", job_id=req["uniqueID"])
        self.write(result.id)


class ZipHandler(BaseHandler, ABC):
    @gen.coroutine
    def get(self, uniqueID):
        self.set_header("Content-Type", "application/zip")
        self.set_header("Content-Disposition", "attachment")
        folder_path = os.path.join(settings.location, uniqueID)
        filename = os.path.join(folder_path, uniqueID + ".zip")
        chunk_size = 1024 * 1024 * 1
        with open(filename, 'rb') as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                try:
                    self.write(chunk)
                    yield self.flush()
                except iostream.StreamClosedError:
                    break
                finally:
                    del chunk
                    yield gen.sleep(0.000000001)


class CheckStatusHandler(BaseHandler, ABC):
    @gen.coroutine
    def get(self, uniqueID):
        job = Job.fetch(uniqueID, connection=r)
        folder_path = os.path.join(settings.location, uniqueID)
        file_path = os.path.join(folder_path, "DIANN", "progress.txt")
        job_status = job.get_status(refresh=True)
        self.set_header("Access-Control-Expose-Headers", "Job-Status")
        self.set_header("Job-Status", job_status)
        if job_status == "started":

            if os.path.exists(file_path):
                with open(file_path, "r") as infile:
                    self.write(infile.read())
            else:
                self.set_status(404)
                self.write("Not exists")
        elif job_status == "finished":
            self.set_header("job-status", "finished")
            with open(file_path, "r") as infile:
                self.write(infile.read())
        elif job_status == "queued":
            self.set_header("job-status", "queued")
            self.write("queued")