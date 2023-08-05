import requests, json, traceback, openai
from flask import request
import loggerutility as logger

class openAI:
    def getCompletionEndpoint(self):
        try:
            jsonData = request.get_data('jsonData', None)
            jsonData = json.loads(jsonData[9:])
            logger.log(f"jsonData openAI class::: {jsonData}","0")

            licenseKey   = jsonData['license_key']
            insightInput = jsonData['insight_input']
            openai.api_key = licenseKey
            openAI_trainingData = open("openAI_trainingData.txt","r").read()
            
            response = openai.Completion.create(
            model="code-davinci-001",
            prompt= openAI_trainingData + insightInput,
            temperature=0.25,
            max_tokens=198,
            top_p=0.5,
            frequency_penalty=0,
            presence_penalty=0,
            stop=["\n"]
            )
            logger.log(f"Response openAI completion endpoint::::: {response}","0")
            finalResult=str(response["choices"][0]["text"])
            logger.log(f"OpenAI completion endpoint finalResult ::::: {finalResult}","0")
            return finalResult
        
        except Exception as e:
            logger.log(f'\n In getCompletionEndpoint exception stacktrace : ', "1")
            trace = traceback.format_exc()
            descr = str(e)
            returnErr = self.getErrorXml(descr, trace)
            logger.log(f'\n Print exception returnSring inside getCompletionEndpoint : {returnErr}', "0")
            return str(returnErr)

    def getErrorXml(self, descr, trace):
        errorXml = '''<Root>
                            <Header>
                                <editFlag>null</editFlag>
                            </Header>
                            <Errors>
                                <error type="E">
                                    <message><![CDATA['''+descr+''']]></message>
                                    <trace><![CDATA['''+trace+''']]></trace>
                                    <type>E</type>
                                </error>
                            </Errors>
                        </Root>'''

        return errorXml


        
