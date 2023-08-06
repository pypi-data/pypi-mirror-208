import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

/**
 * Initialization data for the JupyterGPT extension.
 */
const plugin: JupyterFrontEndPlugin<void> = {
  id: 'JupyterGPT:plugin',
  autoStart: true,
  activate: (app: JupyterFrontEnd) => {
    console.log('JupyterLab extension JupyterGPT is activated!');
  }
};

export default plugin;
