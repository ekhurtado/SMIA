// File: MyPropertiesProvider.js
import { TextFieldEntry, isTextFieldEntryEdited,
  SelectEntry, isSelectEntryEdited,
  Group, ListGroup, ListEntry, ListItem,
} from '@bpmn-io/properties-panel';

import { useService } from 'bpmn-js-properties-panel'


export default class SMIAPropertiesProvider {
  constructor(propertiesPanel, injector, translate) {
    this._translate = translate;
    propertiesPanel.registerProvider(500, this);
  }

  getGroups(element) {
    return (groups) => {
      if (element.type === 'bpmn:ServiceTask') {
        groups.push(this._createSMIAGroup(element));


        groups.push(this._createSMIARequestsGroup(element));
      }

      // Add timeout gateway properties
      if (element.type === 'bpmn:ExclusiveGateway' &&
          element.businessObject.get('smia:isTimeoutGateway')) {
        groups.push(this._createSMIATimeoutGroup(element));
      }

      return groups;
    };
  }

  _createSMIAGroup(element) {
    return {
      id: 'smia-custom-group',
      label: this._translate('SMIA Capability Group'),
      entries: [
        {
          id: 'capability',
          component: CapabilityEntry,
          isEdited: isSelectEntryEdited,
          element
        },
        {
          id: 'constraints',
          component: ConstraintsEntry,
          isEdited: isTextFieldEntryEdited,
          element
        },
        {
          id: 'skill',
          component: SkillEntry,
          isEdited: isSelectEntryEdited,
          element
        },
        {
          id: 'skillParameters',
          component: SkillParametersEntry,
          isEdited: isTextFieldEntryEdited,
          element
        },
        {
          id: 'asset',
          component: AssetEntry,
          isEdited: isSelectEntryEdited,
          element
        }
      ]
    };
  }

  // -------------------
  // Timeout-related code
  // -------------------
  _createSMIARequestsGroup(element) {
    return {
      id: 'smia-requests-group',
      label: this._translate('SMIA Requests group'),
      entries: [
        {
          id: 'requestToPrevious',
          component: RequestToPreviousEntry,
          isEdited: isTextFieldEntryEdited,
          element
        },
        {
          id: 'requestToFollowing',
          component: RequestToFollowingEntry,
          isEdited: isTextFieldEntryEdited,
          element
        }
      ]
    };
  }

  // -------------------
  // Timeout-related code
  // -------------------
  _createSMIATimeoutGroup(element) {
    return {
      id: 'smia-timeout-group',
      label: this._translate('SMIA Timeout group'),
      entries: [
        {
          id: 'timeoutValue',
          component: TimeoutEntry,
          isEdited: isTextFieldEntryEdited,
          element
        // },
        // {
        //   id: 'timeoutExpression',
        //   component: TimeoutExpressionEntry,
        //   isEdited: isTextFieldEntryEdited,
        //   element
        }
      ]
    };
  }



}

SMIAPropertiesProvider.$inject = ['propertiesPanel', 'injector', 'translate'];

// ---------------------------
// CSS-related Entry functions
// ---------------------------
// Componente para capability
function CapabilityEntry(props) {

  // Añadir valores predeterminados para las opciones de la prop3
  // var CAPABILITIES_OPTIONS = [
  //   { value: 'capID001', label: 'Capability 1' },
  //   { value: 'capID002', label: 'Capability 2' },
  //   { value: 'capID003', label: 'Capability 3' }
  // ];

  const { element } = props;
  const translate = useService('translate');
  const commandStack = useService('commandStack');
  const debounce = useService('debounceInput');

  let CAPABILITIES_OPTIONS = [];
  // Obtenemos las posibles capabilities desde los datos obtenidos desde SMIA KB
  if (window.SMIA_KB_DATA.length === 0) {
    CAPABILITIES_OPTIONS = [{value: '', label: ''}]
  } else {
    CAPABILITIES_OPTIONS = window.SMIA_KB_DATA.Capabilities.map((capItem) => {
      return {value: capItem.iri, label: capItem.name}
    });
  }

  const getValue = () => {
    return element.businessObject.get('smia:capability') || '';
  };

  const setValue = (value) => {
    commandStack.execute('element.updateModdleProperties', {
      element,
      moddleElement: element.businessObject,
      // When the capability selection is changed the other data need to be reinitialized
      properties: {
        'smia:capability': value , 'smia:skill': undefined, 'smia:constraints': undefined, 'smia:asset': undefined
      }
    });
  };

  const getOptions = () => {
    return CAPABILITIES_OPTIONS.map(option => ({
      ...option,
      label: translate(option.label)
    }));
  };

  return SelectEntry({
    element,
    id: 'capability',
    label: translate('Capability'),
    tooltip: translate('By choosing a Capability, the related capabilities and asset will be updated.'),
    getValue,
    setValue,
    debounce,
    getOptions
  });
}

// Componente para Prop2 (similar a Prop1)
// Función principal para el grupo Prop2
function ConstraintsEntry(props) {

  const {element} = props;
  const translate = useService('translate');
  const commandStack = useService('commandStack');
  const bpmnFactory = useService('bpmnFactory');

  // Obtenemos la capacidad seleccionada por el usuario, y sus constraints asociados
  let CONSTRAINTS_VALUES = {};
  const capSelection = element.businessObject.get('smia:capability') || '';
  if (capSelection === '') {
    CONSTRAINTS_VALUES = {}
  } else {
    if ('Capabilities' in window.SMIA_KB_DATA) {
      CONSTRAINTS_VALUES = window.SMIA_KB_DATA.Capabilities.reduce((result, capItem) => {
        // uso de reduce para construir el JSON gradualmente
        if ((capItem.iri === capSelection) && (capItem.isRestrictedBy.length > 0)) {
          capItem.isRestrictedBy.forEach((constraintItem) => {
            result[constraintItem.iri] = {'label': constraintItem.name, 'value': ''};
          })
        }
        return result;
      }, {});
    } else { CONSTRAINTS_VALUES = {} }
  }

  // Solo añadimos constraints si existen
  if (JSON.stringify(CONSTRAINTS_VALUES) !== '{}') {
    // Obtener y parsear valores actuales
    const constraints = parseStringWithDelimiters(element.businessObject.get('smia:constraints') || '');

    return Object.keys(CONSTRAINTS_VALUES).map((key, index) => {

      return TextFieldEntry({
        element,
        id: `constraint-${index}`, // Key única basada en índice
        label: translate(CONSTRAINTS_VALUES[key].label),
        tooltip: translate('In this TextField you can add the value of the Capability Constraint.'),
        getValue: () => constraints[key] || '',
        setValue: (value) => {
          const newConstraints = {...constraints, [key]: value};
          commandStack.execute('element.updateModdleProperties', {
            element,
            moddleElement: element.businessObject,
            properties: {'smia:constraints': serializeJSONToStringWithDelimiters(newConstraints)}
          });
        },
        debounce: useService('debounceInput')
      });
    });
  }

}

// Componente para skill
function SkillEntry(props) {

  // Añadir valores predeterminados para las opciones de la prop3
  // let SKILLS_OPTIONS = [
  //   { value: 'skill1', label: 'Skill 1' },
  //   { value: 'skill2', label: 'Skill 2' },
  //   { value: 'skill3', label: 'Skill 3' }
  // ];

  const { element } = props;
  const translate = useService('translate');
  const commandStack = useService('commandStack');
  const debounce = useService('debounceInput');

  // Obtenemos la capacidad seleccionada por el usuario, y sus skills asociadas
  let SKILLS_OPTIONS = [];
  const capSelection = element.businessObject.get('smia:capability') || '';
  if (capSelection === '') {
    SKILLS_OPTIONS = [{value: '', label: ''}]
  } else {
    if ('Capabilities' in window.SMIA_KB_DATA) {
      SKILLS_OPTIONS = window.SMIA_KB_DATA.Capabilities.map((capItem) => {
        if (capItem.iri === capSelection) {
          return capItem.isRealizedBy.map((skillIRI) => {
            const associatedSkill = window.SMIA_KB_DATA.Skills.find(skillItem =>
                skillItem.iri === skillIRI
            );
            return associatedSkill ? {value: associatedSkill.iri, label: associatedSkill.name} : null;
          })
        }
        return null;
      })
          .filter(item => item !== null)
          .flat() || [];
    } else { SKILLS_OPTIONS = [{value: '', label: ''}] }
  }

  const getValue = () => {
    return element.businessObject.get('smia:skill') || '';
  };

  const setValue = (value) => {
    commandStack.execute('element.updateModdleProperties', {
      element,
      moddleElement: element.businessObject,
      // When the skill selection is changed the associated data need to be reinitialized
      properties: { 'smia:skill': value , 'smia:skillParameters': undefined}
      // properties: { 'smia:skill': value }
    });
  };

  const getOptions = () => {
    return SKILLS_OPTIONS.map(option => ({
      ...option,
      label: translate(option.label)
    }));
  };

  return SelectEntry({
    element,
    id: 'skill',
    label: translate('Skill'),
    tooltip: translate('By choosing a Skill, the related skill parameters will be shown in order to add the values.'),
    getValue,
    setValue,
    debounce,
    getOptions
  });
}

// Componente para skill parameter
function SkillParametersEntry(props) {


  const {element} = props;
  const translate = useService('translate');
  const commandStack = useService('commandStack');
  const bpmnFactory = useService('bpmnFactory');

  // Obtenemos la capacidad seleccionada por el usuario, y sus constraints asociados
  let SKILL_PARAMS_VALUES = {};
  const skillSelection = element.businessObject.get('smia:skill') || '';
  if (skillSelection === '') {
    SKILL_PARAMS_VALUES = {};
  } else {
    if ('Capabilities' in window.SMIA_KB_DATA) {
      SKILL_PARAMS_VALUES = window.SMIA_KB_DATA.Capabilities.reduce((result, capItem) => {
        // uso de reduce para construir el JSON gradualmente
        capItem.isRealizedBy.forEach((skillIRI) => {
          if (skillIRI === skillSelection) {
            const associatedSkill = window.SMIA_KB_DATA.Skills.find(skillItem =>
                skillItem.iri === skillIRI
            );
            if (associatedSkill.hasParameter.length > 0) {
              associatedSkill.hasParameter.forEach((skillParamItem) => {
                result[skillParamItem.iri] = {'label': skillParamItem.name, 'value': ''};
              });
            }
          }
        })
        return result;
      }, {});
    } else { SKILL_PARAMS_VALUES = {} }
  }

  // Solo añadimos constraints si existen
  if (JSON.stringify(SKILL_PARAMS_VALUES) !== '{}') {
    // Obtener y parsear valores actuales
    const currentParams = parseStringWithDelimiters(element.businessObject.get('smia:skillParameters') || '');

    return Object.keys(SKILL_PARAMS_VALUES).map((key, index) => {

      return TextFieldEntry({
        element,
        id: `skill-parameter-${index}`, // Key única basada en índice
        label: translate(SKILL_PARAMS_VALUES[key].label),
        tooltip: translate('In this TextField you can add the value of the Skill Parameter.'),
        getValue: () => currentParams[key] || '',
        setValue: (value) => {
          const newCurrentParams = {...currentParams, [key]: value};
          commandStack.execute('element.updateModdleProperties', {
            element,
            moddleElement: element.businessObject,
            properties: {'smia:skillParameters': serializeJSONToStringWithDelimiters(newCurrentParams)}
          });
        },
        debounce: useService('debounceInput')
      });
    });
  }

}

// Componente para prop3 con el menú desplegable
function AssetEntry(props) {

  // Añadir valores predeterminados para las opciones de la prop3
  // const PROPS3_OPTIONS = [
  //   { value: '', label: '' },
  //   { value: 'asset1', label: 'Asset 001' },
  //   { value: 'asset2', label: 'Asset 002' }
  // ];


  const { element } = props;
  const translate = useService('translate');
  const commandStack = useService('commandStack');
  const debounce = useService('debounceInput');

  // Obtenemos la capacidad seleccionada por el usuario, y sus assets asociados
  let ASSETS_OPTIONS = [];
  const capSelection = element.businessObject.get('smia:capability') || '';
  if (capSelection === '') {
    ASSETS_OPTIONS = [{value: '', label: ''}]
  } else {
    if ('Capabilities' in window.SMIA_KB_DATA) {
      ASSETS_OPTIONS = window.SMIA_KB_DATA.Capabilities.map((capItem) => {
        if (capItem.iri === capSelection) {
          return capItem.assets.map((assetItem) => {
            return {value: assetItem.id, label: assetItem.id}
          })
        }
        return null;
      })
          .filter(item => item !== null)
          .flat() || [];
    } else { ASSETS_OPTIONS= [{value: '', label: ''}]}
  }

  const getValue = () => {
    return element.businessObject.get('smia:asset') || '';
  };

  const setValue = (value) => {
    commandStack.execute('element.updateModdleProperties', {
      element,
      moddleElement: element.businessObject,
      properties: { 'smia:asset': value }
    });
  };

  const getOptions = () => {
    return ASSETS_OPTIONS.map(option => ({
      ...option,
      label: translate(option.label)
    }));
  };

  return SelectEntry({
    element,
    id: 'asset',
    label: translate('Asset'),
    tooltip: translate('You can choose a specific asset to perform the capability (or leave it without values to specify none).'),
    getValue,
    setValue,
    debounce,
    getOptions
  });
}


// ----------------------------
// SMIA-related Entry functions
// ----------------------------
function RequestToPreviousEntry(props) {

  const { element } = props;
  const translate = useService('translate');
  const commandStack = useService('commandStack');
  const debounce = useService('debounceInput');

  const getValue = () => {
    return element.businessObject.get('smia:requestToPrevious') || '';
  };

  const setValue = (value) => {
    commandStack.execute('element.updateModdleProperties', {
      element,
      moddleElement: element.businessObject,
      properties: { 'smia:requestToPrevious': value }
    });
  };

  return TextFieldEntry({
    element,
    id: 'requestToPrevious',
    label: translate('requestToPrevious (separated by ";")'),
    placeholder: 'elem[attrib];elem[attrib]',
    tooltip: translate('Each data will be requested to the previous SMIA instance in the flow (e.g. with a reference to an AAS element). Follow "element[attribute]" (e.g. SkillParameter[myParamName]). Elements can be: Capability,CapabilityConstraint,Skill,SkillParameter,Asset.'),
    getValue,
    setValue,
    debounce
  });
}

function RequestToFollowingEntry(props) {

  const { element } = props;
  const translate = useService('translate');
  const commandStack = useService('commandStack');
  const debounce = useService('debounceInput');

  const getValue = () => {
    return element.businessObject.get('smia:requestToFollowing') || '';
  };

  const setValue = (value) => {
    commandStack.execute('element.updateModdleProperties', {
      element,
      moddleElement: element.businessObject,
      properties: { 'smia:requestToFollowing': value }
    });
  };

  return TextFieldEntry({
    element,
    id: 'requestToFollowing',
    label: translate('requestToFollowing (separated by \';\')'),
    placeholder: 'elem[attrib];elem[attrib]',
    tooltip: translate('Each data will be requested to the following SMIA instance in the flow (e.g. with a reference to an AAS element). Follow "element[attribute]" (e.g. SkillParameter[myParamName]). Elements can be: Capability,CapabilityConstraint,Skill,SkillParameter,Asset.'),
    getValue,
    setValue,
    debounce
  });
}

// -----
function TimeoutEntry(props) {
  const { element } = props;
  const translate = useService('translate');
  const commandStack = useService('commandStack');
  const debounce = useService('debounceInput');

  const getValue = () => {
    return element.businessObject.get('smia:timeoutValue') || '10';
  };

  const setValue = (value) => {
    const numValue = parseInt(value, 10);
    if (!isNaN(numValue) && numValue > 0) {
      commandStack.execute('element.updateModdleProperties', {
        element,
        moddleElement: element.businessObject,
        properties: { 'smia:timeoutValue': numValue }
      });
    }
  };

  return TextFieldEntry({
    element,
    id: 'timeoutValue',
    label: translate('Timeout (seconds)'),
    getValue,
    setValue,
    debounce
  });
}


// Useful functions
// ----------------
function parseStringWithDelimiters(stringToParse) {
  return (stringToParse || "").split(';').reduce((acc, pair) => {
    const [key, value] = pair.split('=').map(s => s.trim());
    if (key) acc[key] = value || ""; // Acepta claves sin valor
    return acc;
  }, {});
}

function serializeJSONToStringWithDelimiters(jsonObject) {
  return Object.entries(jsonObject)
      .map(([k, v]) => `${k}=${v || ''}`)
      // .map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(v || '')}`)
      .join(';');
}

SMIAPropertiesProvider.$inject = ['propertiesPanel', 'injector', 'translate'];