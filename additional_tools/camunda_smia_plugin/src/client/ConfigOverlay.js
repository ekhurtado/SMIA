// Este archivo define el componente de overlay para configurar el plugin:

/* eslint-disable no-unused-vars */
import React, { useState } from 'camunda-modeler-plugin-helpers/react';
import { Overlay, Section } from 'camunda-modeler-plugin-helpers/components';

const OFFSET = { right: 0 };

// we can even use hooks to render into the application
export default function ConfigOverlay({ anchor, initValues, onClose, onRequest }) {
  // const [ enabled, setEnabled ] = useState(initValues.enabled); // Utiliza useState para manejar el estado de activación/desactivación del autoguardado
  // const [ interval, setAutoSaveInterval ] = useState(initValues.interval); // Utiliza useState para manejar el estado de intervalo de tiempo entre autoguardados
  const [ requestText, setRequestText ] = useState(initValues.requestText || ''); // Nuevo estado requestText para almacenar el texto ingresado por el usuario

  // const onSubmit = () => onClose({ enabled, interval });

  // const handleRequest = (e) => {
  //   e.preventDefault();
  //   onRequest(requestText);
  // };
  const handleRequest = () => onRequest(requestText);

  /*
  Estructura del overlay:
    Utiliza componentes Section y Section.Header para estructurar el contenido
    Contiene un formulario con:
      Un checkbox para activar/desactivar el autoguardado
      Un campo numérico para establecer el intervalo en segundos
      Un botón "Save" para guardar la configuración
    Al enviar el formulario, llama a onClose con los nuevos valores
  */

  // we can use the built-in styles, e.g. by adding "btn btn-primary" class names
  return (
    <Overlay anchor={ anchor } onClose={ onClose } offset={ OFFSET }>

      <Section>
        <Section.Header>SMIA KB loader</Section.Header>
        <Section.Body>
          <form id="requestForm" onSubmit={ handleRequest }>
            <div class="form-group">
              <label htmlFor="requestText">KB endpoint (ip:port)</label>
              <input
                type="text"
                className="form-control"
                name="KB endpoint"
                value={requestText}
                onChange={ (event) =>
                  setRequestText(event.target.value)
                }
                placeholder="http://<ip>:<port>"
              />
            </div>
          </form>

          <Section.Actions>
            <button
              type="submit"
              className="btn btn-primary"
              form="requestForm"
            >
              Request
            </button>
          </Section.Actions>
        </Section.Body>
      </Section>

      {/*TODO AutoSave plugin section (not added in this SMIA plugin version)*/}
      {/*<Section>*/}
      {/*  <Section.Header>Auto save configuration</Section.Header>*/}

      {/*  <Section.Body>*/}
      {/*    <form id="autoSaveConfigForm" onSubmit={ onSubmit }>*/}
      {/*      <div class="form-group">*/}
      {/*        <div class="custom-control custom-checkbox">*/}
      {/*          <input*/}
      {/*            name="enabled"*/}
      {/*            className="custom-control-input"*/}
      {/*            id="enabled"*/}
      {/*            type="checkbox"*/}
      {/*            onChange={ () => setEnabled(!enabled) }*/}
      {/*            value={ enabled }*/}
      {/*            defaultChecked={ enabled } />*/}
      {/*          <label className="custom-control-label" htmlFor="enabled">*/}
      {/*            Enabled*/}
      {/*          </label>*/}
      {/*        </div>*/}
      {/*      </div>*/}
      {/*      <div className="form-group">*/}
      {/*        <label htmlFor="interval">Interval (seconds)</label>*/}
      {/*        <input*/}
      {/*          type="number"*/}
      {/*          className="form-control"*/}
      {/*          name="interval"*/}
      {/*          min="1"*/}
      {/*          value={ interval }*/}
      {/*          onChange={ (event) =>*/}
      {/*            setAutoSaveInterval(Number(event.target.value))*/}
      {/*          }*/}
      {/*        />*/}
      {/*      </div>*/}
      {/*    </form>*/}

      {/*    <Section.Actions>*/}
      {/*      <button*/}
      {/*        type="submit"*/}
      {/*        className="btn btn-primary"*/}
      {/*        form="autoSaveConfigForm"*/}
      {/*      >*/}
      {/*        Save*/}
      {/*      </button>*/}
      {/*    </Section.Actions>*/}
      {/*  </Section.Body>*/}
      {/*</Section>*/}
    </Overlay>
  );
}

