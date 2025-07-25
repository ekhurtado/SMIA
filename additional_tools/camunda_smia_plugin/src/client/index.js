/** 
 * NOTE: This is specifically a registration of a **bpmn-js** extension. If you would like to create another type of plugin 
 * (say a client extension), the structure of the plugin and the function to register it will be slightly different.
 * 
 * Please refer to:
 * Examples plugins - https://github.com/camunda/camunda-modeler-plugins
 * Plugin documentation - https://docs.camunda.io/docs/components/modeler/desktop-modeler/plugins/
 */

import BpmnModeler from 'bpmn-js/lib/Modeler';
import camundaModdleDescriptor from 'camunda-bpmn-moddle/resources/camunda.json';
//import camundaModdleDescriptor from '../resources/camunda.json';

import { registerClientExtension, registerBpmnJSPlugin, registerBpmnJSModdleExtension } from 'camunda-modeler-plugin-helpers';

import SMIAPlugin from './SMIAPlugin';
import smiaPaletteProviderModule from './smiaPaletteProviders';
import smiaPropertiesProviderModule from './smiaPropertiesProviders';
import smiaPropertiesDescriptor from './smiaPropertiesProviders/properties/smiaPropertiesDescriptor.json';


// Registramos el plugin para configuracion de la interfaz para el usuario
registerClientExtension(SMIAPlugin);

// Registramos el plugin para añadir nuevos ServiceTask para capacidades basadas en CSS model.
registerBpmnJSPlugin(smiaPaletteProviderModule);

// Registramos el plugin para añadir las nuevas secciones a los ServiceTasks nuevos
registerBpmnJSPlugin(smiaPropertiesProviderModule);

// Registramos el descriptor con la definicion de la nueva seccion de SMIA en los ServiceTasks
registerBpmnJSModdleExtension(smiaPropertiesDescriptor);



// import SMIA_KB_OLD_DATA from '../resources/smia_kb_data.json';
// try {
//     if (SMIA_KB_OLD_DATA.length > 0) {
//         window.SMIA_KB_DATA = SMIA_KB_OLD_DATA;
//     }
// } catch (e) {
//   console.log('SMIA KB JSON file does not exist:' + e);
// }
if ('smia-kb-current-data' in localStorage) {
    // The SMIA KB data is updated with old data if available. If there are capabilities already configured and the
    // connection with the SMIA KB has not been realized, it can present errors
    window.SMIA_KB_DATA = JSON.parse(localStorage.getItem('smia-kb-current-data'));
} else {
    localStorage.setItem('smia-kb-current-data', []);
}


// const modeler = new BpmnModeler({
//   additionalModules: [],
//   //moddleExtensions: {
//   moddleExtensions: JSON.parse(JSON.stringify({
//   	camunda: camundaModdleDescriptor
//         //camunda: JSON.parse(JSON.stringify(camundaModdleDescriptor))
//   }))
// });

// console.log("Moddle Extensions Loaded:", modeler.get('moddle').typeMap);
// console.log("Camunda Moddle Descriptor:", camundaModdleDescriptor);

// const moddle = modeler.get('moddle');
// console.log("Moddle Extensions Loaded:", moddle);
// console.log("Registered packages:", moddle.registry.packageMap);
// console.log("Available types:", Object.keys(moddle.registry.typeMap || {}));

// setTimeout(() => {
// 	console.log("Verificando moddleExtensions en el modelador:", modeler.get('moddle'));
// 	console.log("Moddle Extensions Loaded:", modeler.get('moddle')?.typeMap);
// 	modeler.get('moddle').registry.registerPackage(camundaModdleDescriptor);
//   	console.log("Moddle Extensions Loaded:", modeler.get('moddle').typeMap);
// }, 2000);

