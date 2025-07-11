import SMIAPropertiesProvider from './smiaPropertiesProvider';
import SMIAModdleDescriptor from './properties/smiaPropertiesDescriptor.json';

export default {
  __init__: [ 'smiaPropertiesProvider' ],
  smiaPropertiesProvider: [ 'type', SMIAPropertiesProvider ],
  moddleExtensions: {
        smia: SMIAModdleDescriptor
    }
};