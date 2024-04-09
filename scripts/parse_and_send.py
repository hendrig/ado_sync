import re
from gherkin3.parser import Parser
import requests

def convert_and_send(filepath, headers, organization, project_name):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    parser = Parser()
    feature = parser.parse(content)

    for test in feature["scenarioDefinitions"]:
        convertedSteps = ""
        convertedExamples = ""
        convertedParams = ""
        test_name = test["name"]

        if(len(test["steps"]) > 0):
            convertedSteps = convert_step_to_xml(test["steps"])

        if(test.get("examples") is not None):
            convertedExamples = convert_gherkin_examples_to_xml(test["examples"])
            convertedParams = convert_gherkin_parameters(test["examples"])

        json_list = []

        json_title = {
            "op": "replace",
            "path": "/fields/System.Title",
            "value": test_name.encode("utf-8").decode("utf-8")
        }
        json_list.append(json_title)
        json_steps = {
            "op": "replace",
            "path": "/fields/Microsoft.VSTS.TCM.Steps",
            "value": convertedSteps
        }
        json_list.append(json_steps)

        if convertedExamples is not None and convertedExamples != "":
            json_examples = {
                "op": "replace",
                "path": "/fields/Microsoft.VSTS.TCM.LocalDataSource",
                "value": convertedExamples
            }
            json_list.append(json_examples)

        if convertedParams is not None and convertedParams != "":
            json_params = {
                "op": "replace",
                "path": "/fields/Microsoft.VSTS.TCM.Parameters",
                "value": convertedParams
            }
            json_list.append(json_params)

        json_links = build_linked_items(get_links_by_tags(test["tags"]), organization, project_name)
        if len(json_links) > 0:
            for json_link in json_links:
                json_list.append(json_link)

        automation_status = "Not Automated"

        if any(value["name"].startswith('@automated') for value in test["tags"]):
            automation_status = "Automated"

        automation_json =  {
                "op": "replace",
                "path": "/fields/Custom.AutomationStatus",
                "value": automation_status,
            }

        json_list.append(automation_json)

        for wi in get_test_case_by_tags(test["tags"]):
            url = f"https://dev.azure.com/{organization}/_apis/wit/workItems/{wi}?api-version=7.1-preview.3"
            response = requests.patch(url, headers=headers, json=json_list)

            # Check if the request was successful
            if response.status_code == 200:
                print(f"Test case {wi} ({test_name}) synced successfully.")
            else:
                print(f"Failed to create test case {wi}. Error:", response.text)

def build_linked_items(linked_work_items, organization_name, project_name):
    """
    Builds the linked items for updating Azure Test Cases.

    Args:
        linked_work_items (list): List of linked work items.
        organization_name (str): Azure DevOps organization name.
        project_name (str): Azure DevOps project name.

    Returns:
        list: List of linked items for Azure Test Cases.
    """
    linked_items = []

    for linked_item in linked_work_items:
        linked_items.append(
            {
                "op": "add",
                "path": "/relations/-",
                "value": {
                    "rel": "Microsoft.VSTS.Common.TestedBy-Reverse",
                    "url": (
                        f"https://dev.azure.com/{organization_name}/"
                        f"{project_name}/_apis/wit/workitems/{linked_item}"
                    ),
                    "attributes": {"comment": "Associated test case with work item"},
                },
            }
        )

    return linked_items

def get_test_case_by_tags(tags):
    extracted_values = []

    # Iterate over the values of the dictionary
    for value in tags:
        x = value["name"]
        # Check if the value starts with "@tc:"
        if x.startswith('@tc:'):
            # Extract the value after "@tc:"
            extracted_value = x.split('@tc:')[1]
            extracted_values.append(extracted_value)
    
    return extracted_values

def get_links_by_tags(tags):
    extracted_values = []

    # Iterate over the values of the dictionary
    for value in tags:
        x = value["name"]
        if x.startswith('@story:'):
            extracted_value = x.split('@story:')[1]
            extracted_values.append(extracted_value)
        elif x.startswith("@bug:"):
            extracted_value = x.split('@bug:')[1]
            extracted_values.append(extracted_value)
        elif x.startswith("@defect:"):
            extracted_value = x.split('@defect:')[1]
            extracted_values.append(extracted_value)
        elif x.startswith("@wi:"):
            extracted_value = x.split('@wi:')[1]
            extracted_values.append(extracted_value)
    
    return extracted_values

def convert_gherkin_parameters(gherkin_testcase):
    parameters = []

    for option in gherkin_testcase[0]["tableHeader"]["cells"]:
        param_element = f'<param name=\"{option["value"]}\" bind=\"default\"/>'
        parameters.append(param_element)

    paramToSend = f"<parameters>"
    paramToSend += '\n'.join(parameters)
    paramToSend += f"</parameters>"

    return paramToSend

def convert_gherkin_examples_to_xml(gherkin_examples):
    header_elements = []

    header_cell = []

    for option in gherkin_examples[0]["tableHeader"]["cells"]:
        header_element = f"<xs:element name='{option['value']}' type='xs:string' minOccurs='0' />"
        header_elements.append(header_element)
        header_cell.append(option['value'])

    header = f"""<xs:schema id='NewDataSet' xmlns:xs='http://www.w3.org/2001/XMLSchema' xmlns:msdata='urn:schemas-microsoft-com:xml-msdata'>
    <xs:element name='NewDataSet' msdata:IsDataSet='true' msdata:Locale=''>
        <xs:complexType>
            <xs:choice minOccurs='0' maxOccurs = 'unbounded'>
                <xs:element name='Table1'>
                    <xs:complexType>
                        <xs:sequence>"""
    header += '\n'.join(header_elements)
    header += f"""</xs:sequence>
                        </xs:complexType>
                    </xs:element>
                </xs:choice>
            </xs:complexType>
        </xs:element>
    </xs:schema>"""

    body_elements = []
    for body_item in gherkin_examples[0]["tableBody"]:
        body_element = ""
        for i, el in enumerate(body_item["cells"]):
            body_element += f"<{header_cell[i]}>{el['value']}</{header_cell[i]}>"
        body_element = f"<Table1>{body_element}</Table1>"
        body_elements.append(body_element)
    
    dataset = f"<NewDataSet>{header}{body_elements}</NewDataSet>"

    return dataset

def convert_step_to_xml(steps):
    pattern = r'<(.*?)>'
    xml_steps = []
    for idx, step in enumerate(steps, start=2):
        stepText = re.sub(pattern, r'@\1', step["text"]).replace("&", "&amp;")
        xml_step = f'<step id="{idx}" type="ActionStep">\n'
        xml_step += f'    <parameterizedString isformatted="true">&lt;DIV&gt;&lt;P&gt;&lt;B&gt;{step["keyword"]}&lt;/B&gt; {stepText}&lt;/P&gt;&lt;/DIV&gt;</parameterizedString>\n'
        xml_step += '    <parameterizedString isformatted="true">&lt;DIV&gt;&lt;P&gt;&lt;BR/&gt;&lt;/P&gt;&lt;/DIV&gt;</parameterizedString>\n'
        xml_step += '    <description/>\n'
        xml_step += '</step>'
        xml_steps.append(xml_step)

    xml = f'<steps id="0" last="{idx}">\n'
    xml += '\n'.join(xml_steps)
    xml += '\n</steps>'

    return xml