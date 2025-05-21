import { format } from 'react-string-format';

import BpmnModeler from 'bpmn-js/lib/Modeler';
import camundaModdleDescriptor from 'camunda-bpmn-moddle/resources/camunda.json';
import smiaModdleDescriptor from '../smiaPropertiesProviders/properties/smiaPropertiesDescriptor.json';

/**
 * A palette that allows you to create BPMN _and_ custom elements.
 */

const lblAasWebServ = 'Create a SMIA ServiceTask out of ';
const lblTimeoutGateway = 'Create a SMIA Timeout Gateway of ';
var CUSTOM_PALETTE = {};

const smiaLogoSVG = `
<svg width="91" height="32" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" xml:space="preserve" overflow="hidden"><defs><clipPath id="clip0"><rect x="172" y="639" width="91" height="32"/></clipPath><image width="101" height="55" xlink:href="data:image/png;base64,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" preserveAspectRatio="none" id="img1"></image><clipPath id="clip2"><rect x="0" y="34957.2" width="554784" height="193613"/></clipPath></defs><g clip-path="url(#clip0)" transform="translate(-172 -639)"><g transform="matrix(0.000164028 0 0 0.000164028 172 639)"><g clip-path="url(#clip2)" transform="matrix(1 0 0 1.00762 -0.0358806 -35223.9)"><use width="100%" height="100%" xlink:href="#img1" transform="scale(5492.91 5492.91)"></use></g></g></g></svg>
`;

export default class SMIAPaletteProvider {

	constructor(palette, create, elementFactory, bpmnFactory, translate) {
	    // Se añaden las dependencias y configuración inicial
	    this._palette = palette;
	    CUSTOM_PALETTE = this._palette;
	    CUSTOM_PALETTE.Actions = {};
	    CUSTOM_PALETTE.NSMIAsFound = 0;
	    CUSTOM_PALETTE.SMIADiscovererStatus = 'READY';
	    this._create = create;
	    this._bpmnFactory = bpmnFactory;
	    this._elementFactory = elementFactory;
	    this._translate = translate;

	    const modeler = new BpmnModeler({
			  additionalModules: [],
			  moddleExtensions: {
				  camunda: camundaModdleDescriptor,
				  smia: smiaModdleDescriptor
			        //camunda: JSON.parse(JSON.stringify(camundaModdleDescriptor))
			  }
			});
			this._moddle = modeler.get('moddle');

	    palette.registerProvider(this);
	}

	getPaletteEntries() {


    	// Metodo principal que devuelve las entradas para la paleta de herramientas
		var create = this._create,
        elementFactory = this._elementFactory,
        bpmnFactory = this._bpmnFactory,
        moddle = this._moddle;

  		// Prueba: vamos a crear nuevos ServiceTasks
    	CUSTOM_PALETTE.Actions.SMIAServicesGroupSeparator = {
			group: 'SMIAServicesGroup',
			separator: true
		};

		// Add the group header with icon
		CUSTOM_PALETTE.Actions['smia-group-header'] = {
			group: 'SMIAServicesGroup',
			// html: '<img src="../../resources/SMIA_logo_vertical.svg" alt="SMIA logo" />',
			// html: '<img src="../../resources/SMIA_logo_vertical.svg" alt="SMIA logo" />',
			html: '<div class="group-header">' + smiaLogoSVG + '</div>',
			className: 'smia-header-logo'
		};

		// Prueba, se añade un nuevo ServiceTask al grupo creado
		// let randomID = [...Array(5)].map(() => Math.random().toString(36)[2]).join('').toUpperCase();
		var modelerPlugs = {create, bpmnFactory, elementFactory, moddle}
		CUSTOM_PALETTE.Actions['capabilityServiceTask'] = {
	    group: 'SMIAServicesGroup',
	    className: 'bpmn-icon-service-task smia-capability-service-task',
	    title: lblAasWebServ + 'capability',
	    action: {
	    	dragstart: createSMIAServiceTask(modelerPlugs, 'Capability', 'capID', 'urn:aas:001', 'my_aas_test'),
	      	click: createSMIAServiceTask(modelerPlugs, 'Capability', 'capID', 'urn:aas:001', 'my_aas_test')
	    }
		}

		// Añadir el nuevo Timeout Gateway al grupo SMIA (para eventos)
		CUSTOM_PALETTE.Actions['smiaTimeoutGateway'] = {
			group: 'SMIAServicesGroup',
			className: 'bpmn-icon-gateway-xor smia-timeout-gateway', // Usar el icono XOR gateway por defecto
			title: lblTimeoutGateway + 'event',
			action: {
				dragstart: createSMIATimeoutGateway(modelerPlugs),
				click: createSMIATimeoutGateway(modelerPlugs)
			}
		}
  		

	    // Forzar la actualización visual de la paleta
	    // CUSTOM_PALETTE._update();
    
    	return CUSTOM_PALETTE.Actions; 
  }
}

// Define las dependencias que deben ser inyectadas por el contenedor DI (Dependency Injection) de bpmn-js
SMIAPaletteProvider.$inject = [
  'palette',
  'create',
  'elementFactory',
  'bpmnFactory',
  'translate'
];

// Tooling functions
function createSMIAServiceTask(modelerPlugs, name, id, aasIdentifier, aasIdShort) {

  	// Crea una tarea de servicio (ServiceTask) BPMN con de momento a mano
  	const {create, bpmnFactory, elementFactory, moddle} = modelerPlugs;

  	return function (event) {

		  const randomID = createRandomID();

		  const serviceTask = elementFactory.createShape({
			  type: "bpmn:ServiceTask"
		  });
		  const extensionElements = moddle.create('bpmn:ExtensionElements');

		  const payloadInputParameter = moddle.create('camunda:InputParameter', {
			  name: 'payload',
			  value: 'payload'
		  });
		  // Crear el contenedor de inputOutput
		  const inputOutput = moddle.create('camunda:InputOutput', {
			  inputParameters: [payloadInputParameter],
			  outputParameters: []
		  });

		  var connector = moddle.create("camunda:Connector", {
			  connectorId: "http-connector", inputOutput
		  });

		  const testProperty = moddle.create('camunda:Property', {
			  name: 'testName',
			  value: 'testValue'
		  });

		  const testProperty3 = moddle.create('camunda:Property', {
			  name: 'testName3',
			  value: 'testValue3'
		  });


		  const camundaProperties = moddle.create('camunda:Properties', {
			  name: 'sadddsada',
			  values: [testProperty, testProperty3]
		  });

		  const testProperty2 = moddle.create('camunda:Property', {
			  name: 'testName2',
			  value: 'testValue2'
		  });

		  const camundaProperties2 = moddle.create('camunda:Properties', {
			  name: 'as',
			  values: [testProperty2]
		  });


		  extensionElements.values = [connector, camundaProperties, camundaProperties2];

		  serviceTask.businessObject.extensionElements = extensionElements;

		  // Set to the businessObject
		  serviceTask.businessObject.name = `Capability ${randomID}`;
		  serviceTask.businessObject.id = `cap_${randomID}`;
		  serviceTask.businessObject.taskType = 'smiaTask';

		  // Set SMIA specific properties ??? (de momento esta comentado, probar si hace falta)
		  // serviceTask.businessObject.set('smia:capability', '');
		  // serviceTask.businessObject.set('smia:constraints', '');
		  // serviceTask.businessObject.set('smia:skill', '');
		  // serviceTask.businessObject.set('smia:skillParameters', '');
		  // serviceTask.businessObject.set('smia:asset', '');

		  create.start(event, serviceTask);
  	};
}

// Función para crear el nuevo Timeout Gateway
function createSMIATimeoutGateway(modelerPlugs) {
	const {create, bpmnFactory, elementFactory, moddle} = modelerPlugs;

	return function(event) {
		// Crear un gateway exclusivo (XOR)
		const gateway = elementFactory.createShape({
			type: 'bpmn:ExclusiveGateway'
		});

		// Añadir extensión de elementos para metadata
		const extensionElements = moddle.create('bpmn:ExtensionElements');

		// Crear propiedades Camunda para el timeout
		const timeoutProperty = moddle.create('camunda:Property', {
			name: 'timeoutValue',
			value: '30' // Valor por defecto de 30 segundos
		});

		const camundaProperties = moddle.create('camunda:Properties', {
			name: 'timeoutConfiguration',
			values: [timeoutProperty]
		});

		extensionElements.values = [camundaProperties];

		gateway.businessObject.extensionElements = extensionElements;

		// Establecer propiedades del gateway
		gateway.businessObject.name = 'Timeout Gateway';
		gateway.businessObject.id = 'TimeoutGateway_' + Math.floor(Math.random() * 10000);

		// Establecer propiedades SMIA personalizadas
		gateway.businessObject.set('smia:isTimeoutGateway', true);
		gateway.businessObject.set('smia:timeout', 30); // Valor por defecto 30 segundos

		// Iniciar la creación
		create.start(event, gateway);
	};
}

// Funcion para crear un ID random
function createRandomID() {
	return [...Array(5)].map(() => Math.random().toString(36)[2]).join('').toUpperCase();
}