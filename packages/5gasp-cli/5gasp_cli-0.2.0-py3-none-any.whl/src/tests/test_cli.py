# -*- coding: utf-8 -*-
# @Author: Eduardo Santos
# @Date:   2023-02-10 17:15:58
# @Last Modified by:   Eduardo Santos
# @Last Modified time: 2023-03-14 17:41:45

import typer
from typer.testing import CliRunner

from main import app
from main import infer_tags

runner = CliRunner()

#def test_cli():
#    '''
#    Test CLI
#    '''
#    result = runner.invoke(app, [
#                                "create-tests", 
#                                "--config-file", 
#                                "../../resources/config.yaml",
#                                "--infer-tags-from-nsd",
#                                "../../resources/hackfest_multivdu_nsd.yaml"]
#                            )
#    
#    tags = ["{{hackfest_multivdu-ns|hackfest_multivdu-vnf|vnf-mgmt-ext}}", 
#            "{{hackfest_multivdu-ns|hackfest_multivdu-vnf|vnf-data-ext}}",
#            "{{hackfest_multivdu-ns|hackfest_multivdu-vnf|vnf-mgmt-ext}}",
#            "{{hackfest_multivdu-ns|hackfest_multivdu-vnf|vnf-data-ext}}"]
#            
#    #assert result.exit_code == 0
#    for tag in tags:
#        assert tag in result.stdout

def test_infer_tags():
    output = infer_tags(["tests/resources/hackfest_multivdu_nsd.yaml"])

    tags = set(["{{hackfest_multivdu-ns|hackfest_multivdu-vnf|vnf-mgmt-ext}}", 
            "{{hackfest_multivdu-ns|hackfest_multivdu-vnf|vnf-data-ext}}",
            "{{hackfest_multivdu-ns|hackfest_multivdu-vnf|vnf-mgmt-ext}}",
            "{{hackfest_multivdu-ns|hackfest_multivdu-vnf|vnf-data-ext}}"])
            
    #assert result.exit_code == 0
    for tag in tags:
        assert tag in output