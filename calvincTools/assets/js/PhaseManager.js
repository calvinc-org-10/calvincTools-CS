// ?? change Phase -> phases ??

// The State Manager Class
class PhaseManager {
 /* use later??
  #phases;
  #current;
  #history = [];
  #onChange;
 */
 
  /**
   * @param {Object} phaseDefinitions   Frozen object of phase key -> phase value
   * @param {*} initialPhase            A value from phaseDefinitions to start on (defaults to the first one)
   * @param {Object} [options]
   * @param {HTMLElement} [options.phaseInput]         Element whose .value shows the current phase
   * @param {HTMLElement} [options.phasesCompleteList] <ul>/<ol> element to append completed phases to
   */
  constructor(phaseDefinitions, initialPhase = null, options = {}) {

    // Permit either:
    // - an ordered array: ["start", "upload", "done"]
    // - a definition object: { START: "start", UPLOAD: "upload", DONE: "done" }
    const phases = Array.isArray(phaseDefinitions)
      ? [...phaseDefinitions]
      : Object.values(phaseDefinitions);

    if (phases.length === 0) {
      throw new Error("PhaseManager requires at least one phase.");
    }

    if (new Set(phases).size !== phases.length) {
      throw new Error("Each phase value must be unique.");
    }

    this.phaseDefinitions = phaseDefinitions;
    this.Phase = Object.freeze(phases);
    
    this.current = initialPhase ?? this.Phase[0];

    if (!this.Phase.includes(this.current)) {
      throw new Error(`Invalid initial phase: ${initialPhase}`);
    }

    // Optional DOM hooks, injected rather than assumed as globals
    this.phaseInput = options.phaseInput ?? null;
    this.phasesCompleteList = options.phasesCompleteList ?? null;

    this.showCurrentPhase();
  }

  // Get current phase
  get() {
    return this.current;
  }

  // Get current position index
  get index() {
    return this.Phase.indexOf(this.current);
  }

  get phases() {
    return this.Phase;
  }

  /**
  get completed() {
    return this.#history.map(({ from }) => from);
  }
  **/

  get isFirst() {
    return this.index === 0;
  }

  get isFinal() {
    return this.index === this.Phase.length - 1;
  }

  get nextPhase() {
    return this.Phase[this.index + 1] ?? null;
  }

  get previousPhase() {
    return this.Phase[this.index - 1] ?? null;
  }

  // Skip directly to any specific phase safely
  skipTo(targetPhase) {
    if (!this.Phase.includes(targetPhase)) {
      throw new Error(`Invalid phase: ${targetPhase}`);
    }

    if (targetPhase === this.current) {
      return this.current;
    }        

    this.listCompletedPhase()
    this.current = targetPhase;
    this.showCurrentPhase();

    return this.current;
  }

  // Advance by 1 step
  next() {
    if (this.isFinal) {
      return this.current;
    }

    return this.skipTo(this.nextPhase);
  }

  // Check if a specific phase has already been passed
  hasPassed(targetPhase) {
    const targetIndex = this.Phase.indexOf(targetPhase);
    if (targetIndex === -1) {
      throw new Error(`Invalid phase: ${targetPhase}`);
    }
    return this.index > targetIndex;
  }

  // Get the text of a specific phase (currently just returns the raw value;
  // swap in a lookup table here if you want human-readable labels)
  getPhaseText(targetPhase = this.current) {
    if (this.Phase.includes(targetPhase)) {
      return targetPhase;
    } else {
      throw new Error(`Invalid phase: ${targetPhase}`);
    }
  }
  
  // show completed phase in HTML element
  listCompletedPhase() {
    const element = this.phasesCompleteList;

    if (element) {
        const li = document.createElement("li");
        li.textContent = this.getPhaseText(this.current);
        element.appendChild(li);
    }
  }
  // show current phase in HTML element
  showCurrentPhase() {
    const element = this.phaseInput;

    if (element) {
        element.value = this.getPhaseText(this.current);
    }
  }
}
