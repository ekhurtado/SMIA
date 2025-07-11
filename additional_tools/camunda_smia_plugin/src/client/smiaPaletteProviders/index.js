import SMIAPaletteProvider from './SMIAPaletteProvider';

import BpmnModeler from 'bpmn-js/lib/Modeler';
import camundaModdleDescriptor from 'camunda-bpmn-moddle/resources/camunda.json';

const modeler = new BpmnModeler({
  additionalModules: [],
  //moddleExtensions: {
  moddleExtensions: JSON.parse(JSON.stringify({
    camunda: camundaModdleDescriptor
        //camunda: JSON.parse(JSON.stringify(camundaModdleDescriptor))
  }))
});

export default {
  __init__: [ 'SMIAPaletteProvider' ],
  SMIAPaletteProvider: [ 'type', SMIAPaletteProvider ]
};