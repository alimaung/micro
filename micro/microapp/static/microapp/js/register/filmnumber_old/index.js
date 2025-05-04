/**
 * Film Number Allocation Main Module
 * 
 * This is the main entry point for the film number allocation step.
 * It imports all other modules and initializes the application.
 */

import * as FilmNumberCore from './core.js';

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', FilmNumberCore.init); 