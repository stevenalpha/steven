__author__ = 'steven.alpha'
__version__ = '1.0'
__project__ = 'https://github.com/stevenalpha/steven'

import os
import time
import socket
import hashlib
import urllib
import urllib2


class HTTPSQS():
    """
    low level httpsqs.
    A httpsqs server should be running first
    httpsqs project : http://code.google.com/p/httpsqs/
    """
    @staticmethod
    def get_http_content(url_target, data_post=None,  timeout=30):
        opener = urllib2.build_opener()
        urllib2.install_opener(opener)
        request = urllib2.Request(url_target, data=data_post)
        r = ''
        try:
            f = urllib2.urlopen(request, timeout=timeout)
            r = f.read()
        except urllib2.HTTPError, e1:
            print e1
        except urllib2.URLError, e2:
            print e2
        except socket.timeout, e3:
            print e3
        except Exception, e:
            print e
        finally:
            pass
        return r


    @staticmethod
    def get(queue_name, queue_host, queue_port, queue_charset, queue_password, queue_timeout):
        """
        get one item from queue,
        curl "http://host:port/?charset=utf-8&name=your_queue_name&opt=get&auth=mypass123"
        :param queue_name:queue name
        :param queue_host: queue server's address
        :param queue_port:queue server's port
        :param queue_charset:charset for communicate
        :param queue_password:password for authentication
        :param queue_timeout:timeout for http request
        :return:string content got from queue server
        """
        url_target = "http://%s:%s/?charset=%s&name=%s&opt=get&auth=%s" % (queue_host,
                                                                           queue_port,
                                                                           queue_charset,
                                                                           queue_name,
                                                                           queue_password)
        return HTTPSQS.get_http_content(url_target, timeout=queue_timeout)



    @staticmethod
    def put(queue_name, queue_data, queue_host, queue_port, queue_charset, queue_password, queue_timeout):
        """
        put one item to queue
        curl "http://host:port/?name=your_queue_name&opt=put&data=urlencodemsg&auth=mypass123
        :param queue_name:string
        :param queue_data:json json data for post
        :param queue_host:string server name or ip address
        :param queue_port:integer
        :param queue_charset:string
        :param queue_password:string
        :param queue_timeout:integer
        :return:string
        """
        url_target = "http://%s:%d/?charset=%s&name=%s&opt=put&auth=%s" % (queue_host,
                                                                           queue_port,
                                                                           queue_charset,
                                                                           queue_name,
                                                                           queue_password)
        data_post = urllib.urlencode({'data':queue_data})[5:]
        return HTTPSQS.get_http_content(url_target, data_post, timeout=queue_timeout)


    @staticmethod
    def status(queue_name, queue_host, queue_port, queue_password, queue_timeout):
        """
        get status of queue
        curl "http://host:port/?name=your_queue_name&opt=status_json&auth=mypass123"
        :param queue_name:string
        :param queue_host:string server name or ip address
        :param queue_port:integer
        :param queue_charset:string
        :param queue_timeout:integer
        :return:string
        """
        url_target = "http://%s:%d/?name=%s&opt=status_json&auth=%s" % (queue_host,
                                                                        queue_port,
                                                                        queue_name,
                                                                        queue_password)
        return HTTPSQS.get_http_content(url_target, timeout=queue_timeout)


    @staticmethod
    def reset(queue_name, queue_host, queue_port, queue_password, queue_timeout):
        """
        reset a queue
        curl "http://host:port/?name=your_queue_name&opt=reset&auth=mypass123"
        :param queue_name:string
        :param queue_host:string server name or ip address
        :param queue_port:integer
        :param queue_charset:string
        :param queue_password:string
        :param queue_timeout:integer
        :return:string
        """
        url_target = "http://%s:%d/?name=%s&opt=reset&auth=%s" % (queue_host,
                                                                  queue_port,
                                                                  queue_name,
                                                                  queue_password)
        return HTTPSQS.get_http_content(url_target, timeout=queue_timeout)


class HQ():
    """high level httpsqs"""
    queue_host     = '1.2.3.4'
    queue_port     = 1218
    queue_password = 'CHANGE_ME_TO_YOUR_PASSWORD'
    queue_charset  = 'utf-8'
    queue_timeout  = 30


    @staticmethod
    def put(queue_name, item):
        """
        put item to queue
        :param queue_name: queue name
        :param item:  item to put
        :return: True or False
        """
        return HTTPSQS.put(queue_name, item, HQ.queue_host, HQ.queue_port,
                           HQ.queue_charset, HQ.queue_password, HQ.queue_timeout) == 'HTTPSQS_PUT_OK'

    @staticmethod
    def get(queue_name):
        """
        get item from queue
        :param queue_name:string
        :return:string
        """
        item = HTTPSQS.get(queue_name, HQ.queue_host, HQ.queue_port,
                           HQ.queue_charset, HQ.queue_password, HQ.queue_timeout)
        if 'HTTPSQS_GET_END' == item\
                or 'HTTPSQS_AUTH_FAILED' == item\
                or 'HTTPSQS_ERROR' == item:
            return ''
        else:
            return item


    @staticmethod
    def status(queue_name):
        """
        return status of httpsqs queue
        :param queue_name:string
        :return:string
        """
        return HTTPSQS.status(queue_name, HQ.queue_host, HQ.queue_port,
                              HQ.queue_password, HQ.queue_timeout).strip()

    @staticmethod
    def reset(queue_name):
        """
        reset a queue
        :param queue_name:string
        :return:bool
        """
        return HTTPSQS.reset(queue_name, HQ.queue_host, HQ.queue_port,
                             HQ.queue_password, HQ.queue_timeout) == 'HTTPSQS_RESET_OK'

    @staticmethod
    def unread(queue_name):
        """
        return how many unread message in a given queue name
        :param queue_name:string
        :return:int
        """
        unread = 0
        status = HTTPSQS.status(queue_name, HQ.queue_host, HQ.queue_port,
                                HQ.queue_password, HQ.queue_timeout)
        if status.find('unread') > -1:
            try:
                unread = int(status.split('"unread":')[-1].split('}')[0])
            except:
                unread = -1
        return unread



class TLD():
    '''
    # Source path of Mozilla's effective TLD names file.
    http://mxr.mozilla.org/mozilla/source/netwerk/dns/src/effective_tld_names.dat?raw=1
    '''
    __tld__data__file__   = '.' + os.path.sep + 'res' + os.path.sep + 'effective_tld_names.dat'
    tld_names_list        = []
    tld_data_loaded       = False


    @staticmethod
    def init_tld_names_list():
        try:
            fhandle            = open(TLD.__tld__data__file__)
            TLD.tld_names_list = set([line.strip() for line in fhandle if line[0] not in '/\n'])
        except Exception, e:
            print e
        finally:
            try:
                fhandle.close()
            except Exception, e2:
                print e2
            finally:
                if len(TLD.tld_names_list) > 0:
                    TLD.tld_data_loaded = True

    @staticmethod
    def parse(domain, active_only=True):
        '''
        input :test-04.videos.google.jp.co
        output:('example', 'com.cn', 'example.com.cn', 'mail.example.com.cn')
        '''
        if TLD.tld_data_loaded  == False:
            TLD.init_tld_names_list()

        domain_parts = domain.split('.')
        for i in range(0, len(domain_parts)):
            sliced_domain_parts = domain_parts[i:]

            match = '.'.join(sliced_domain_parts)
            wildcard_match = '.'.join(['*'] + sliced_domain_parts[1:])
            inactive_match = "!%s" % match

            # Match tlds
            if (match in TLD.tld_names_list or
                wildcard_match in TLD.tld_names_list or
                (active_only is False and inactive_match in TLD.tld_names_list) ):
                return (domain_parts[i-1], ".".join(domain_parts[i:]), ".".join(domain_parts[i-1:]), domain)
        return '', '', '', ''


    @staticmethod
    def get_tld_name(domain):
        """
        return the key word of domain, for example:
        test-04.videos.google.com -> google
        :param domain:string
        :return:string
        """
        return TLD.parse(domain)[0]


class C():
    EMERG  = 7
    ALERT  = 6
    CRIT   = 5
    ERROR  = 4
    WARN   = 3
    NOTICE = 2
    INFO   = 1
    DEBUG  = 0


    priority = {7: 'EMERG', 6: 'ALERT', 5: 'CRIT', 4: 'ERROR',
                3: 'WARN', 2: 'NOTICE', 1: 'INFO', 0: 'DEBUG'}

    @staticmethod
    def info(msg, pri=1):
        if pri >= C.check_debug_level():
            msg = '[%s][%s]:%s' % (C.priority[pri], time.strftime('%Y-%m-%d %H:%M:%S'), msg)
            print msg

    @staticmethod
    def check_debug_level():
        """
        create an file named debug.info, then will filter message whose pri is lower than information
        :return:
        """
        if os.path.exists('debug.%s' % C.priority[0].lower()) :return C.EMERG
        if os.path.exists('debug.%s' % C.priority[1].lower()) :return C.ALERT
        if os.path.exists('debug.%s' % C.priority[2].lower()) :return C.CRIT
        if os.path.exists('debug.%s' % C.priority[3].lower()) :return C.ERROR
        if os.path.exists('debug.%s' % C.priority[4].lower()) :return C.WARN
        if os.path.exists('debug.%s' % C.priority[5].lower()) :return C.NOTICE
        if os.path.exists('debug.%s' % C.priority[7].lower()) :return C.DEBUG
        return C.INFO

class MD5():
    """MD5 function string to hex"""
    def __init__(self):
        self.__init__()

    @staticmethod
    def md5(raw_message):
        """
        return md5 value of a given string
        md5 string length  is 32 as default
        :param raw_message:
        :return:
        """
        md5_str = ''
        md5c = hashlib.md5()
        md5c.update(raw_message)
        md5_str = md5c.hexdigest()
        return md5_str

    @staticmethod
    def md5_16(raw_message):
        """
        return md5 value of a given string
        md5 string length  is 16
        :param raw_message:
        :return:
        """
        return MD5.md5(raw_message)[8:24]

if __name__ == '__main__':
    print MD5.md5('123456')
    print MD5.md5_16('123456')

    C.info('test')
    C.info('test', C.ERROR)

    domain = 'test-04.videos.google.co.jp'

    print TLD.get_tld_name(domain)
    print TLD.parse(domain)

    HQ.queue_host = 'example.httpsqs-server.com'
    HQ.queue_password = 'xxoo123'
    print HQ.put('test', 'test content')
    print HQ.status('test')
    print HQ.unread('test')
    print HQ.get('test')
    print HQ.reset('test')