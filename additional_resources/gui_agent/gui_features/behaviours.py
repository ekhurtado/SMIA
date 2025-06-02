import calendar
import json
import time
from json import JSONDecodeError
from urllib.parse import parse_qs

from spade.behaviour import OneShotBehaviour, CyclicBehaviour
from spade.message import Message


class GUIAgentBehaviours:

    class SendBehaviour(OneShotBehaviour):
        async def run(self):
            # Prepare the ACL message
            if isinstance(self.msg_data, str):
                data_json = {k: v[0] if len(v) == 1 else v for k, v in parse_qs(self.msg_data).items()}
            else:
                data_json = self.msg_data
            print(data_json)

            # Create the Message object
            print("Building the message to send to the agent with JID: " + str(data_json['receiver']))
            receiver = data_json['receiver'] + '@' + data_json['server']
            msg = Message(to=receiver, thread=data_json['thread'])
            msg.set_metadata('performative', data_json['performative'])
            msg.set_metadata('ontology', data_json['ontology'])
            msg.set_metadata('encoding', 'application/json')    # TODO DE MOMENTO SIEMPRE ES JSON (se usan JSONSchemas)
            msg.set_metadata('language', 'smia-language')    # TODO DE MOMENTO SIEMPRE ES ESTE VALOR

            if 'protocol' in data_json:
                msg.set_metadata('protocol', data_json['protocol'])

            # Now the body of the ACL-SMIA message is built
            msg_body_json = None
            match data_json['ontology']:
                case 'asset-related-service' | 'agent-related-service':
                    # TODO recoger los atributos para este caso
                    try:
                        msg_body_json = {'serviceRef': json.loads(data_json['serviceRefARS'])}
                    except JSONDecodeError as e:
                        # ModelReference can also be added as string
                        # If [] has been added with separation, it must be removed
                        msg_body_json = {'serviceRef': data_json['serviceRefARS'].replace('] [', '][').strip()}
                    if 'serviceParamsARS' in data_json:
                        msg_body_json.update({'serviceParams': json.loads(data_json['serviceParamsARS'])})
                case 'aas-service':
                    # TODO recoger los atributos para este caso
                    msg_body_json = {'serviceID': data_json['serviceIDAS'],
                                     'serviceType': data_json['serviceTypeAS']}
                    if 'serviceParamsAS' in data_json:
                        try:
                            msg_body_json.update({'serviceParams': json.loads(data_json['serviceParamsAS'])})
                        except JSONDecodeError as e:
                            msg_body_json.update({'serviceParams': data_json['serviceParamsAS'].replace('] [', '][').strip()})

                case 'aas-infrastructure-service':
                    # TODO recoger los atributos para este caso
                    msg_body_json = {'serviceID': data_json['serviceIDAIS'],
                                     'serviceType': data_json['serviceTypeAIS']}
                    if 'serviceParamsAIS' in data_json:
                        msg_body_json.update({'serviceParams': json.loads(data_json['serviceParamsAIS'])})
                case 'css-service':
                    msg_body_json = {'capabilityIRI': data_json['capabilityIRI']}
                    if 'skillIRI' in data_json:
                        msg_body_json.update({'skillIRI': data_json['skillIRI']})
                    if 'constraints' in data_json:
                        msg_body_json.update({'constraints': json.loads(data_json['constraints'])})
                    if 'skillParams' in data_json:
                        msg_body_json.update({'skillParams': json.loads(data_json['skillParams'])})
                    if 'skillInterfaceIRI' in data_json:
                        msg_body_json.update({'skillInterfaceIRI': data_json['skillInterfaceIRI']})
                    if 'negCriterion' in data_json:
                        msg_body_json.update({'negCriterion': data_json['negCriterion']})
                        # The requester of the negotiation need to be added too
                        msg_body_json.update({'negRequester': str(self.agent.jid)})
                    if 'negTargets' in data_json:
                        processed_targets = []
                        for target in data_json['negTargets'].split(','):
                            if '@' not in target:
                                target = target + '@' + data_json['server']
                            processed_targets.append(target)
                        msg_body_json.update({'negTargets': processed_targets})
                case _:
                    if 'normalMessage' in data_json:
                        msg.body = data_json['normalMessage']
                    else:
                        msg.body = ''
            print(json.dumps(msg_body_json))
            if 'normalMessage' not in data_json:
                msg.body = json.dumps(msg_body_json)
            print(msg)

            print("Sending the message...")
            await self.send(msg)
            print("Message sent!")

    class SendBehaviour_v0(OneShotBehaviour):
        async def run(self):
            # Prepare the ACL message
            if isinstance(self.msg_data, str):
                data_json = {k: v[0] if len(v) == 1 else v for k, v in parse_qs(self.msg_data).items()}
            else:
                data_json = self.msg_data
            print(data_json)

            # Create the Message object
            print("Building the message to send to the agent with JID: " + str(data_json['receiver']))
            receiver = data_json['receiver'] + '@' + data_json['server']
            msg = Message(to=receiver, thread=data_json['thread'])
            msg.set_metadata('performative', data_json['performative'])
            msg.set_metadata('ontology', data_json['ontology'])

            if data_json['messageType'] == 'normal':  # message body with normal format
                msg.body = data_json['normalMessage']
            elif 'acl' in data_json['messageType']:
            # elif len(data_json['messageType']) == 2:
                msg_body_json = {'serviceID': data_json['serviceID'],
                                 'serviceType': data_json['serviceType'],
                                 'serviceData': {
                                     'serviceCategory': data_json['serviceCategory']
                                 }
                                 }
                if 'serviceParams' in data_json:
                    msg_body_json['serviceData']['serviceParams'] = json.loads(data_json['serviceParams'])
                # '", "serviceParams": ' + data_json['serviceParams'] + '}}
                print(json.dumps(msg_body_json))
                msg.body = json.dumps(msg_body_json)
            print(msg)

            print("Sending the message...")
            await self.send(msg)
            print("Message sent!")

    class NegBehaviour(OneShotBehaviour):

        async def run(self):
            # Prepare the ACL message
            data_json = {k: v[0] if len(v) == 1 else v for k, v in parse_qs(self.msg_data).items()}
            print(data_json)

            # Create the Message object
            # TODO mirar como se envian las negociaciones
            if ',' in data_json['receiver']:
                receivers_jid = data_json['receiver'].split(',')
            else:
                receivers_jid = [data_json['receiver']]

            for i in range(0, len(receivers_jid)):
                receivers_jid[i] = receivers_jid[i] + '@' + data_json['server']
            print("targets updated with XMPP server")


            for jid in receivers_jid:
                print("Building the negotiation message to send to the agent with JID: " + jid)
                msg = Message(to=jid, thread=data_json['thread'])
                msg.set_metadata('performative', data_json['performative'])
                msg.set_metadata('ontology', data_json['ontology'])
                # msg.set_metadata('neg_requester_jid', str(self.agent.jid))
                # msg.set_metadata('targets', str(receivers_jid))
                # msg.body = data_json['criteria']

                # Now the negotiation are sent as request of an AgentCapability
                # TODO Msg structure of I4.0 SMIA
                msg_body_json = {
                    'serviceID': 'startNegotiation',
                    'serviceType': 'CSSRelatedService',   # TODO pensar que tipo de servicio es el de negociacion
                    'serviceData': {
                        'serviceCategory': 'service-request',
                        'timestamp': calendar.timegm(time.gmtime()),
                        'serviceParams': {
                            'neg_requester_jid': str(self.agent.jid),
                            'capabilityName': 'Negotiation',
                            'skillName': data_json['criteria'],
                            'targets': ','.join(receivers_jid)
                        }
                    }
                }
                msg.body = json.dumps(msg_body_json)

                print(msg)

                print("Sending the message...")
                await self.send(msg)
                print("Message sent!")

            print("All negotiation messages sent!")

    class ReceiverBehaviour(CyclicBehaviour):

        async def run(self):
            msg = await self.receive(timeout=10)  # Wait for a message for 10 seconds
            if msg:
                msg_body_json = json.loads(msg.body)
                msg_body_json['sender'] = msg.sender
                msg_body_json['thread'] = msg.thread
                msg_body_json['performative'] = msg.get_metadata('performative')
                self.agent.acl_msg_log.append(msg_body_json)
                print(f"Message received: {msg.body}")
            # else:
            #     print("No msg")


