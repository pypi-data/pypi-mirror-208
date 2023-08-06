import datetime
from btweb.logger import Logger
import os
import re
import requests
from requests.auth import HTTPBasicAuth
import sys

logger = Logger().init_logger(__name__)


class WebAdapter:

  def __init__(self, **kwargs):
    self.fail_on_errors = kwargs.get('fail_on_errors')
    self.verify_tls = kwargs.get('verify_tls', True)
    caller = sys._getframe(1).f_globals.get('__name__', 'N/A')
    logger.debug('Module imported by %s', caller)

  def write_cache_file(self, response_obj, cache_file_path):

    if not os.path.isfile(cache_file_path):
      try:
        with open(cache_file_path, 'wb') as f:
            for chunk in response_obj.iter_content(chunk_size=1024): 
                if chunk:
                    f.write(chunk)
        logger.info('Wrote cache file at %s' % cache_file_path)
      except Exception as e:
        logger.warning("Failed to cache content at {url}, error code was {code}".format(
          url=url,
          code=response_obj.status_code
          )
        )

  def get(self, url, **kwargs):

    username = kwargs.get('username')
    password = kwargs.get('password') 
    cache = kwargs.get('cache', False)
    cache_path = kwargs.get('cache_path', '/tmp')
    cache_time_limit = kwargs.get('cache_time', 60)
    timeout = kwargs.get('timeout')

    try:
      response = requests.get(
        url, 
        auth=HTTPBasicAuth(username, password),
        verify=self.verify_tls,
        timeout=timeout
        )
      if username and password:
        response = requests.get(
          url, 
          auth=HTTPBasicAuth(username, password),
          verify=self.verify_tls,
          timeout=timeout          
        )
      else:
        response = requests.get(
        url,
        verify=self.verify_tls,
        timeout=timeout
        )
    except Exception as e:
        err_message = "Connection to {url} failed with error {err}".format(
          url=url,
          err=e
        )
        if self.fail_on_errors:
          raise Exception(err_message)
        else:
          logger.error(err_message)
          return

    if response.status_code == 200:
      if cache:
        content_disposition = response.headers.get('content-disposition')
        if content_disposition:
          remote_filename = re.findall("filename=(.+)", d)[0]
        else:
          remote_filename = url.split('/')[-1]
        cache_file = '%s/%s' % (cache_path, remote_filename)
        if not os.path.isfile(cache_file):
          self.write_cache_file(response, cache_file)
        else:
          logger.info('Found cache file at %s' % cache_file)
          cache_file_modified = datetime.datetime.fromtimestamp(
            os.path.getmtime(cache_file)
            )
          cache_time_limit = datetime.timedelta(minutes=cache_time_limit)
          if datetime.datetime.now() - file_modified > cache_time_limit:
            logger.info('Cache time for file at %s has expired' % cache_file)
            self.write_cache_file(response, cache_file)
          else:
            try:
              cached_content = open(cache_file).read()
            except Exception as e:
              logger.error("Reading cache file {f} failed with error {err}".format(
                f=cache_file,
                err=e
                )
              )
            return
      return(response.text)
    else:
      err_message = "Error: Call to {url} failed with error code {code}".format(
        url=url,
        code=response.status_code
      )
      if self.fail_on_errors:
        raise Exception(err_message)
      else:
        return err_message