/**
 * Copyright Camunda Services GmbH and/or licensed to Camunda Services GmbH
 * under one or more contributor license agreements. See the NOTICE file
 * distributed with this work for additional information regarding copyright
 * ownership.
 *
 * Camunda licenses this file to you under the MIT; you may not use this file
 * except in compliance with the MIT License.
 */

// Este archivo define el componente principal del plugin que implementa la funcionalidad, en este caso, de autoguardado.

/* eslint-disable no-unused-vars*/
import React, { Fragment, PureComponent } from 'camunda-modeler-plugin-helpers/react';
import { Fill } from 'camunda-modeler-plugin-helpers/components';   // el componente Fill permite insertar elementos en slots específicos de la UI

import classNames from 'classnames';

import Icon from '../resources/SMIA_logo_vertical.svg';
import Icon_OK from '../resources/circle-check-solid.svg';
import Icon_ERROR from '../resources/circle-xmark-solid.svg';

let Icon_KB = Icon_OK;

import ConfigOverlay from './ConfigOverlay';

// Import the HTTP utility functions
import {
  checkServerAvailability, httpGetData,
} from './smia-kb-utils';

// Define un estado inicial con valores por defecto (autoguardado desactivado, intervalo de 5 segundos)
const defaultState = {
  enabled: false,
  interval: 5,
  configOpen: false,
  requestText: '',  // para almacenar el texto añadido por el usuario
  showRequestText: false  // para controlar la visibilidad del texto en la interfaz
};

/**
 * An example client extension plugin to enable auto saving functionality
 * into the Camunda Modeler
 */
export default class AutoSavePlugin extends PureComponent {

  constructor(props) {
    super(props);

    this.state = defaultState;

    this.handleConfigClosed = this.handleConfigClosed.bind(this);
    this.handleRequest = this.handleRequest.bind(this);  // metodo para gestionar la seccion request 

    this._buttonRef = React.createRef();

    this.activeTab = {
      id: '__empty',
      type: 'empty'
    };

    this.serverUrl = '';

  }

  componentDidMount() {
    // componentDidMount(): Se ejecuta cuando el componente se inicializa

    /**
    * The component props include everything the Application offers plugins,
    * which includes:
    * - config: save and retrieve information to the local configuration
    * - subscribe: hook into application events, like <tab.saved>, <app.activeTabChanged> ...
    * - triggerAction: execute editor actions, like <save>, <open-diagram> ...
    * - log: log information into the Log panel
    * - displayNotification: show notifications inside the application
    */
    const {
      config,
      subscribe
    } = this.props;

    // retrieve plugin related information from the application configuration
    // Recupera la configuración guardada del plugin
    config.getForPlugin('autoSave', 'config')
      .then(config => this.setState(config));

    // subscribe to the event when the active tab changed in the application
    // Reinicia el temporizador cuando cambia la pestaña activa
    subscribe('app.activeTabChanged', ({ activeTab }) => {
      this.clearTimer();
      this.activeTab = activeTab;

      if (this.state.enabled && activeTab.file && activeTab.file.path) {
        this.setupTimer();
      }
    });

    // subscribe to the event when a tab was saved in the application
    // Reinicia el temporizador después de guardar
    subscribe('tab.saved', () => {
      if (!this.timer && this.state.enabled) {
        this.setupTimer();
      }
    });

    // Se inicializa la variable para almacenar los datos del SMIA KB
    window.SMIA_KB_DATA = []
  }

  componentDidUpdate() {
    const {
      configOpen,
      enabled
    } = this.state;

    if (!enabled || configOpen) {
      this.clearTimer();
    }

    if (!this.timer && !configOpen && enabled && this.activeTab.file && this.activeTab.file.path) {
      this.setupTimer();
    }
  }

  setupTimer() {
    // Configura un temporizador que guarda automáticamente según el intervalo configurado
    this.timer = setTimeout(() => {
      this.save();
      this.setupTimer();
    }, this.state.interval * 1000);
  }

  clearTimer() {
    // Limpia el temporizador existente
    if (this.timer) {
      clearTimeout(this.timer);
      this.timer = null;
    }
  }

  save() {
    // Ejecuta la acción de guardado usando triggerAction('save')
    const {
      displayNotification,
      triggerAction
    } = this.props;

    // trigger a tab save operation
    triggerAction('save')
      .then(tab => {
        if (!tab) {
          return displayNotification({ title: 'Failed to save' });
        }
      });
  }

  handleConfigClosed(newConfig) {
    // Maneja el cierre del diálogo de configuración y guarda los nuevos valores
    this.setState({ configOpen: false });

    if (newConfig) {

      // via <config> it is also possible to save data into the application configuration
      this.props.config.setForPlugin('autoSave', 'config', newConfig)
        .catch(console.error);

      this.setState(newConfig);
    }
  }

  handleRequest(text) {
    // metodo para gestionar la seccion request
    const { displayNotification } = this.props;
    if (!text.includes("http://")) {
      text = "http://" + text
    }
    this.serverUrl = text;
    this.displayInformNotification('SMIA KB availability', 'Trying to connect to SMIA KB in: ' + text);
    // displayNotification({
    //   title: 'SMIA KB availability',
    //   content: 'Trying to connect to SMIA KB in: ' + text,
    //   duration: 5000
    // });

    return new Promise((resolve, reject) => {
        // First, the availability with SMIA KB is checked
        checkServerAvailability(this.serverUrl + '/api/v3/ui/').then(result => {
          if (!result.available) {
            // If server is not available, reject the promise with the reason and stop execution
            // this.displayErrorNotification('ERROR AL CONECTAR CON KB!', 'ERROR AL CONECTAR CON KB: ' + result.reason);
            throw new Error(`SMIA KB is not available. Reason: ${result.reason}`);
          }

          // Once the SMIA KB is available, all the required information will be obtained
          // First, the capability identifiers (IRIs) will be obtained
          // TODO, DE MOMENTO SE HA PENSADO RECOGER LAS IRIs y con eso el resto de datos, pero quizas es suficiente recogiendo todos los objetos JSON de todas las capaciades ('/capabilities'), y procesar todo ello. Si es cierto que las skills habria que recogerlas desde su API, ya que en las capacidades solo estan las referencias (IRIs)
          this.displayInformNotification('CSS Capability identifiers',
              'Obtaining CSS Capability identifiers from SMIA KB');
          return httpGetData(`${this.serverUrl}/api/v3/capabilities/$identifiers`);

        }).then((allCapabilityIDs) => {
          if (allCapabilityIDs.includes("ERROR: ")) {
            throw new Error(`Error while interacting with the SMIA KB (requesting capability identifiers). Reason: ${allCapabilityIDs.replace("ERROR: ", '')}`);
          }
          this.displayInformNotification('CSS Capability identifiers',
              'Obtained data: ' + allCapabilityIDs);

          // TODO DE MOMENTO SE RECOGE DE LA VERSION DE PRUEBAS DE SMIA (mas adelante la respuesta vendra mejor estructurada)
          allCapabilityIDs = allCapabilityIDs.split(': ')[1];
          this.displayInformNotification('CSS Capability identifiers',
              'AHORA SI data: ' + allCapabilityIDs);

          // TODO PENSAR COMO AÑADIR EL CODIGO DE FORMA QUE ITERE SOBRE TODOS LOS IDENTIFICADORES DE CAPACIDADES, Y VARA RECOGIENDO TODA SU INFORMACION (despues se debera hacer lo mismo con las skills).


          // Simulate async logic (e.g., fetching data or processing)
          setTimeout(() => {
            const data = "This is the processed text"; // Replace with actual logic
            displayNotification({
              title: 'Processing...',
              content: 'Segundo mensaje con el contenido de procesando... ' + text,
              duration: 7000
            });

            // TODO Prueba para datos recogidos del SMIA KB=
            // TODO En esta primera version todos los datos de la skill estan dentro de cada capacidad, pero yo creo que
            //  seria mejor tener dos grandes JSON (capacidad y skill), y en el de capacidad tener solo las referencias
            //  a las skills (es decir, seguir la misma estructura que dentro del KB)
            window.SMIA_KB_DATA = [{
              'capID001': {
                'name': 'capability1', 'assetsID': ['asset1', 'asset2'],
                'skills': [{
                  'name': 'skill1_1',
                  'inputParams': ['inputparam1_1', 'inputparam1_2']
                }, {'name': 'skill1_2'}]
              }
            },
              {
                'capID002': {
                  'name': 'capability2', 'assetsID': ['asset3'], 'constraints': ['constraint2_1', 'constraint2_2'],
                  'skills': [{'name': 'skill2_1'}, {'name': 'skill2_2'}]
                }
              }];

            // También actualizar el estado para mostrar el texto en la UI si se desea
            Icon_KB = Icon_OK;  // Una vez finalizado correctamente añadimos el icono de OK con la conexión de SMIA KB
            this.setState({
              showRequestText: true,
              requestText: this.serverUrl
            });

            displayNotification({
              type: 'error',
              title: 'Processing failed...',
              content: 'Mensaje de error... ' + text,
              duration: 7000
            });

            setTimeout(() => {
              this.displayNotificationWithType('Process finished',
                  'All data have been correctly obtained from SMIA KB', 'success');
              resolve(data);
            }, 1000);

          }, 1000);
        }).catch(error => {
          this.displayNotificationWithType('ERROR', 'Some error occured: ' + error, 'error');

          Icon_KB = Icon_ERROR;
            // displayNotification({
            //   type: 'error',
            //   title: 'Processing failed...',
            //   content: 'Mensaje de error... ' + error,
            //   duration: 7000
            // });
          this.setState({
            showRequestText: true,
            requestText: this.serverUrl
          });

          reject(error);
        });
    });
    // -- fin mostrar conexion con KB

  }

  displayInformNotification(title, content, duration=5000) {
    const { displayNotification } = this.props;

    return displayNotification({
      title: title,
      content: content,
      duration: duration
    });
  }

  displayNotificationWithType(title, content, type ,duration=5000) {
    const { displayNotification } = this.props;

    return displayNotification({
      type: type,
      title: title,
      content: content,
      duration: duration
    });
  }

  // handleRequest(text) {
  //   // metodo para gestionar la seccion request
  //   const { displayNotification } = this.props;
  //
  //   displayNotification({
  //     title: 'Primer mensaje...',
  //     content: 'Primer mensaje con su contenido... ' + text,
  //     duration: 7000
  //   });
  //   console.log("Haciendo algo");
  //   displayNotification({
  //     title: 'Segundo mensaje...',
  //     content: 'Segundo mensaje con su contenido... ' + text,
  //     duration: 7000
  //   });
  //
  //
  //   // Mostrar conexion con la KB mencionando que se esta recogiendo la informacion de SMIA relacionada con el CSS model
  //   displayNotification({
  //     title: 'Connecting with SMIA KB...',
  //     content: 'Trying to connect with the SMIA KB located in ' + text,
  //     duration: 7000
  //   }).then(() => {
  //
  //   // Segunda notificación (después de que termine la primera)
  //   return displayNotification({
  //     title: 'Obtaining SMIA information from KB...',
  //     content: 'SMIA information related to the CSS model is being obtained.',
  //     duration: 10000
  //     });
  //   }).then(() => {
  //
  //   // Tercera notificación
  //
  //   // -- fin mostrar conexion con KB
  //
  //   // Prueba notificacion con acciones
  //   return displayNotification({
  //     title: 'Actualización disponible',
  //     content: '¿Desea actualizar a la nueva versión?',
  //     primaryAction: {
  //       label: 'Actualizar',
  //       handler: () => this.updatePlugin()
  //     },
  //     secondaryAction: {
  //       label: 'No ahora',
  //       handler: () => this.dismissUpdate()
  //     }
  //     });
  //   }).then(() => {
  //   // Ultima notificación (después de que terminen todas las anteriores)
  //
  //   // Mostrar el texto solicitado en una notificación
  //   return displayNotification({
  //     title: 'Request finished',
  //     content: text,
  //     duration: 5000
  //     });
  //   }).catch(error => {
  //     // Manejo de errores
  //     displayNotification({
  //       type: 'error',
  //       title: 'Error',
  //       content: 'An error occurred while processing your request: ' + error.message
  //   });
  //   });
  //
  //   // -- fin mostrar conexion con KB
  //
  //   // TODO Prueba para datos recogidos del SMIA KB=
  //   window.SMIA_KB_DATA = [{'capID001': {'name': 'capability1', 'assetsID': ['asset1', 'asset2'],
  //     'skills': [{'name': 'skill1_1', 'inputParams': ['inputparam1_1', 'inputparam1_2']},{'name': 'skill1_2'}]}},
  //     {'capID002': {'name': 'capability2', 'assetsID': ['asset3'], 'constraints': ['constraint2_1', 'constraint2_2'],
  //         'skills': [{'name': 'skill2_1'},{'name': 'skill2_2'}]}}];
  //
  //   // También actualizar el estado para mostrar el texto en la UI si se desea
  //   this.setState({
  //     showRequestText: true,
  //     requestText: text
  //   });
  // }

  /**
   * render any React component you like to extend the existing
   * Camunda Modeler application UI
   */
  render() {
    const {
      configOpen,
      enabled,
      interval,
      requestText,
      showRequestText
    } = this.state;

    const initValues = {
      enabled,
      interval,
      requestText
    };

    // we can use fills to hook React components into certain places of the UI
    // Utiliza Fill para insertar un botón en la barra de estado de la aplicación (en el footer) y le añade un icono. Al hacer click, se abre la configuración. Renderiza condicionalmente el ConfigOverlay cuando configOpen es true
    return <Fragment>
      <Fill slot="status-bar__app" group="1_autosave">
        <button
          ref={ this._buttonRef }
          className={ classNames('btn', { 'btn--active': configOpen }) }
          onClick={ () => this.setState({ configOpen: true }) }>
          <Icon />
        </button>
      </Fill>

      {/* Mostrar el texto solicitado si showRequestText es true al lado del boton de SMIA */}
      {showRequestText && (
        // <Fill slot="status-bar__app" group="2_requestText">
        //   <div style={{ display: "flex", alignItems: "center" }}>
        //     <Icon_KB />
        //     <span className="status-bar__label">KB:&nbsp;{requestText}</span>
        //   </div>
        // </Fill>
        <Fill slot="status-bar__app" group="2_requestText">
          <div className="smia-kb-conn-div"><Icon_KB /></div>
          {/*<Icon_KB />*/}
          <span className="status-bar__label smia-kb-conn-label"><strong>KB:</strong>&nbsp;{requestText}</span>
        </Fill>
      )}

      { this.state.configOpen && (
        <ConfigOverlay
          anchor={ this._buttonRef.current }
          onClose={ this.handleConfigClosed }
          onRequest={ this.handleRequest }  // Se enlaca el metodo onRequest de 'ConfigOverlay' al metodo handleRequest de 'AutoSavePlugin'
          initValues={ initValues }
        />
      )}
    </Fragment>;
  }
}
