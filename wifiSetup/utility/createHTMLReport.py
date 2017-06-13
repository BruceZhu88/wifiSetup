'''
Created on 2014-11-27

@author: Yoyo.Liu

Edited by Bruce Zhu
'''
__version__='1.0'

import sys, os
import time
import pdb

import unittest
import logging
from xml.sax import saxutils
from distutils.log import INFO


class Template_mixin(object):
    """
    Define a HTML template for report customerization and generation.

    Overall structure of an HTML report

    HTML
    +------------------------+
    |<html>                  |
    |  <head>                |
    |                        |
    |   STYLESHEET           |
    |   +----------------+   |
    |   |                |   |
    |   +----------------+   |
    |                        |
    |  </head>               |
    |                        |
    |  <body>                |
    |                        |
    |   HEADING              |
    |   +----------------+   |
    |   |                |   |
    |   +----------------+   |
    |                        |
    |   REPORT               |
    |   +----------------+   |
    |   |                |   |
    |   +----------------+   |
    |                        |
    |   ENDING               |
    |   +----------------+   |
    |   |                |   |
    |   +----------------+   |
    |                        |
    |  </body>               |
    |</html>                 |
    +------------------------+
    """

    #DEFAULT_TITLE = 'Unit Test Report'
    #DEFAULT_DESCRIPTION = ''

    # ------------------------------------------------------------------------
    # HTML Template

    HTML_TMPL = r"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <title>%(title)s</title>
    <meta name="generator" content="%(generator)s"/>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
    %(stylesheet)s
</head>
<body>                
<script language="javascript" type="text/javascript"><!--
output_list = Array();

/* level - 0:Summary; 1:Failed; 2:All */
function showCase(level) {
    trs = document.getElementsByTagName("tr");
    for (var i = 0; i < trs.length; i++) {
        tr = trs[i];
        id = tr.id;
        if (id.substr(0,2) == 'ft') {
            if (level < 1) {
                tr.className = 'hiddenRow';
            }
            else {
                tr.className = '';
            }
        }
        if (id.substr(0,2) == 'pt') {
            if (level > 1) {
                tr.className = '';
            }
            else {
                tr.className = 'hiddenRow';
            }
        }
    }
}


function showClassDetail(cid, count) {
    var id_list = Array(count);
    var toHide = 1;
    for (var i = 0; i < count; i++) {
        tid0 = 't' + cid.substr(1) + '.' + (i+1);
        tid = 'f' + tid0;
        tr = document.getElementById(tid);
        if (!tr) {
            tid = 'p' + tid0;
            tr = document.getElementById(tid);
        }
        id_list[i] = tid;
        if (tr.className) {
            toHide = 0;
        }
    }
    for (var i = 0; i < count; i++) {
        tid = id_list[i];
        if (toHide) {
            document.getElementById('div_'+tid).style.display = 'none'
            document.getElementById(tid).className = 'hiddenRow';
        }
        else {
            document.getElementById(tid).className = '';
        }
    }
}


function showTestDetail(div_id){
    var details_div = document.getElementById(div_id)
    var displayState = details_div.style.display
    // alert(displayState)
    if (displayState != 'block' ) {
        displayState = 'block'
        details_div.style.display = 'block'
    }
    else {
        details_div.style.display = 'none'
    }
}


function html_escape(s) {
    s = s.replace(/&/g,'&amp;');
    s = s.replace(/</g,'&lt;');
    s = s.replace(/>/g,'&gt;');
    return s;
}

/* obsoleted by detail in <div>
function showOutput(id, name) {
    var w = window.open("", //url
                    name,
                    "resizable,scrollbars,status,width=800,height=450");
    d = w.document;
    d.write("<pre>");
    d.write(html_escape(output_list[id]));
    d.write("\n");
    d.write("<a href='javascript:window.close()'>close</a>\n");
    d.write("</pre>\n");
    d.close();
}
*/
--></script>

%(heading)s
%(report)s
%(ending)s

</body>
</html>
"""

    # variables: (title, generator, stylesheet, heading, report, ending)


    # ------------------------------------------------------------------------
    # Stylesheet
    #
    # alternatively use a <link> for external style sheet, e.g.
    #   <link rel="stylesheet" href="$url" type="text/css">

    STYLESHEET_TMPL = """
<style type="text/css" media="screen">
body        { font-family: verdana, arial, helvetica, sans-serif; font-size: 80%; }
table       { font-size: 100%; }
pre         { }

/* -- heading ---------------------------------------------------------------------- */
h1 {
    font-size: 16pt;
    color: gray;
}
.heading {
    margin-top: 0ex;
    margin-bottom: 1ex;
}

.heading .attribute {
    margin-top: 1ex;
    margin-bottom: 0;
}

.heading .description {
    margin-top: 4ex;
    margin-bottom: 6ex;
}

/* -- css div popup ------------------------------------------------------------------------ */
a.popup_link {
}

a.popup_link:hover {
    color: red;
}

.popup_window {
    display: none;
    position: relative;
    left: 0px;
    top: 0px;
    /*border: solid #627173 1px; */
    padding: 10px;
    background-color: #E6E6D6;
    font-family: "Lucida Console", "Courier New", Courier, monospace;
    text-align: left;
    font-size: 8pt;
    width: 500px;
}

}
/* -- report ------------------------------------------------------------------------ */
#show_detail_line {
    margin-top: 3ex;
    margin-bottom: 1ex;
}
#result_table {
    width: 80%;
    border-collapse: collapse;
    border: 1px solid #777;
}
#header_row {
    font-weight: bold;
    color: white;
    background-color: #777;
}
#result_table td {
    border: 1px solid #777;
    padding: 2px;
}
#total_row  { font-weight: bold; }
.passClass  { background-color: #6c6; }
.failClass  { background-color: #c60; }
.errorClass { background-color: #c00; }
.passCase   { color: #6c6; }
.failCase   { color: #c60; font-weight: bold; }
.errorCase  { color: #c00; font-weight: bold; }
.hiddenRow  { display: none; }
.testcase   { margin-left: 2em; }


/* -- ending ---------------------------------------------------------------------- */
#ending {
}

</style>
"""



    # ------------------------------------------------------------------------
    # Heading
    #

    HEADING_TMPL = """<div class='heading'>
<h1>%(title)s</h1>
%(parameters)s
<p class='description'>%(description)s</p>
</div>

""" # variables: (title, parameters, description)

    HEADING_ATTRIBUTE_TMPL = """<p class='attribute'><strong>%(name)s:</strong> %(value)s</p>
""" # variables: (name, value)



    # ------------------------------------------------------------------------
    # Report
    #

    REPORT_TMPL = """

<table id='result_table'>
<colgroup>
<col align='left' />
<col align='right' />
<col align='right' />
<col align='right' />
<col align='right' />
<col align='right' />
</colgroup>
<tr id='header_row'>
    <td>Test Group/Test case</td>
    <td>Test Result</td>
</tr>
%(test_list)s
</table>
""" # variables: (test_list, count, Pass, fail, error)

    REPORT_CLASS_TMPL = r"""
<tr class='%(style)s'>
    <td>%(desc)s</td>
    <td>%(result)s</td>

</tr>
""" # variables: (style, desc, count, Pass, fail, error, cid)


    REPORT_TEST_WITH_OUTPUT_TMPL = r"""
<tr id='%(tid)s' class='%(Class)s'>
    <td class='%(style)s'><div class='testcase'>%(desc)s</div></td>
    <td colspan='5' align='center'>

    <!--css div popup start-->
    <a class="popup_link" onfocus='this.blur();' href="javascript:showTestDetail('div_%(tid)s')" >
        %(status)s</a>

    <div id='div_%(tid)s' class="popup_window">
        <div style='text-align: right; color:red;cursor:pointer'>
        <a onfocus='this.blur();' onclick="document.getElementById('div_%(tid)s').style.display = 'none' " >
           [x]</a>
        </div>
        <pre>
        %(script)s
        </pre>
    </div>
    <!--css div popup end-->

    </td>
</tr>
""" # variables: (tid, Class, style, desc, status)


    REPORT_TEST_NO_OUTPUT_TMPL = r"""
<tr id='%(tid)s' class='%(Class)s'>
    <td class='%(style)s'><div class='testcase'>%(desc)s</div></td>
    <td colspan='5' align='center'>%(status)s</td>
</tr>
""" # variables: (tid, Class, style, desc, status)


    REPORT_TEST_OUTPUT_TMPL = r"""
%(id)s: %(output)s
""" # variables: (id, output)



    # ------------------------------------------------------------------------
    # ENDING
    #

    ENDING_TMPL = """<div id='ending'>&nbsp;</div>"""

# -------------------- The end of the Template class -------------------

class CreateHTMLRpt(Template_mixin):
    """
    """
    def __init__(self, *argvs):
        #self.stream = sys.stdout
        self.verbosity = 1
        self.filename = argvs[0]
        self.title = argvs[1]
        self.testname = argvs[2]
        self.duration = argvs[3]
        self.cycle = argvs[4]
        self.status = argvs[5]
        self.result = argvs[6]
        
    @classmethod
    def init_report(cls,project_code, root_dir = None):
        #cfg=getTestConfig('testconfig.ini')
        #project_code=cfg['testconfig']['project_code']
        cls.report_conf = cls.make_root_dir(project_code, root_dir)
        
        reportfile = cls.get_report_file("report_" + project_code+ "_" + cls.get_reportger_timestr())
        #print "reportfile: ",reportfile
        report_file_full_name = os.path.join(cls.report_conf['runreport_dir'], reportfile)
        #print "report_file_full_name : ",report_file_full_name 

        reportformat = cls.get_report_format()
        #print "reportformat : ",reportformat 
        cls.report_conf['reportfile'] = reportfile
        
        #print "cls.report_conf: ",cls.report_conf
        return report_file_full_name    

###########################################################################
###########################################################################
    @classmethod
    def make_root_dir(cls, project_code, root_dir = None):
        cls.report_conf = dict(root_run = os.getcwd())
        """
        if not root_dir:
            if os.environ.has_key('AT_Report_DIR'):
                root_dir = os.environ['AT_Report_DIR']
            else:
                root_dir = os.path.realpath(os.path.join(os.getcwd(), "..", 'report'))

        """
        root_dir = os.path.realpath(os.path.join(os.getcwd(), "..", 'report'))
        run_report_dir = os.path.realpath(os.path.join(root_dir, project_code))

        if not os.path.exists(run_report_dir):
            os.makedirs(run_report_dir)

        cls.report_conf['runreport_dir'] = run_report_dir
        return cls.report_conf


    @classmethod
    def get_reportger_timestr(cls):
        return time.strftime("%Y%m%d%H%M")


    @classmethod
    def get_report_format(cls):
        reportformat = '%(asctime)s %(levelname)-8s %(message)s'

        return reportformat


    @classmethod
    def get_report_file(cls, filename_id):
        reportfile = "%s.html" % (filename_id)

        return reportfile


    @classmethod
    def get_report_filename_linux(cls, reportfile_fullname):
        return reportfile_fullname.replace("\\", "/")



###########################################################################
###########################################################################
   

    def getReportAttributes(self):
        """
        Return report attributes as a list of (name, value).
        Override this to add custom attributes.
        """
        return [
            ('Test case', self.testname),
            ('Duration', self.duration),
            ('Runing cycles', self.cycle),
            ('Status', self.status),
        ]


    def createTestHTML(self,filepath):
        htmlPath = os.path.realpath(os.path.join(filepath,self.filename))
        if '.html' not in htmlPath:
            htmlPath += '.html'
        self.description = htmlPath
        self.stream = open(htmlPath, "w")
        report_attrs = self.getReportAttributes()
        generator = 'createHTMLRpt %s' % __version__
        stylesheet = self._generate_stylesheet()
        heading = self._generate_heading(report_attrs)
        report = self._generate_report()
        ending = self._generate_ending()
        output = self.HTML_TMPL % dict(
            title = saxutils.escape(self.title),
            generator = generator,
            stylesheet = stylesheet,
            heading = heading,
            report = report,
            ending = ending,
        )
        self.stream.write(output)
        #self.stream.write(output.encode('utf8'))
        
        if os.path.exists(htmlPath):
            log = 'Create html file "%s" successfully.' %(htmlPath)
            logging.log(INFO, log)
            return htmlPath
        else:
            log = 'Create pdf file "%s" failed.' %(htmlPath)
            logging.log(INFO, log)
            return None


    def _generate_stylesheet(self):
        return self.STYLESHEET_TMPL


    def _generate_heading(self, report_attrs):
        a_lines = []
        for name, value in report_attrs:
            line = self.HEADING_ATTRIBUTE_TMPL % dict(
                    name = saxutils.escape(name),
                    value = saxutils.escape(value),
                )
            a_lines.append(line)
        heading = self.HEADING_TMPL % dict(
            title = saxutils.escape(self.title),
            parameters = ''.join(a_lines),
            description = saxutils.escape(self.description),
        )
        return heading


    def _generate_report(self):
        rows = []
        for key in self.result:
            row = self.REPORT_CLASS_TMPL % dict(
                    style = self.result[key].lower()=='fail' and 'failClass' or 'passClass',
                    desc = key,
                    result = self.result[key],
                )
            rows.append(row)
        report = self.REPORT_TMPL % dict(
            test_list = ''.join(rows)
        )
        return report



    def _generate_ending(self):
        return self.ENDING_TMPL

################################################################################  
    @classmethod    #this "classmethod" must add here
    def report_result(self,title,start_time,duration,cycle,status,update,status1,downgrade,status2,Network_Error,status3):
        report_conf = CreateHTMLRpt.init_report('project.report') 
        lst = [report_conf,title,start_time,duration,cycle,status,{update:status1,downgrade:status2,Network_Error:status3,}]
        '''
        print(len(lst))
        for itme in lst:
            print(itme)
        '''
        report = CreateHTMLRpt(*lst)
        #datas = report.createTestHTML('d:\\')
        datas = report.createTestHTML('')        
        
if __name__ == '__main__':
    CreateHTMLRpt.report_result('CA16 update test','start_time','duration','10','running','1update','update_time','downgrade','downgrade_time','Network_Error','Network_Error')
    
    '''
    report_conf = CreateHTMLRpt.init_report('project.report')
    lst = [report_conf,'title','start time','duration','status',{'1':'pass',' ':' ','2':'pass','3':'fail','4':'fail','5':'fail'}]
    print len(lst)
    for itme in lst:
        print itme
    report = CreateHTMLRpt(*lst)
    #datas = report.createTestHTML('d:\\')
    datas = report.createTestHTML('')
    '''
    


     
