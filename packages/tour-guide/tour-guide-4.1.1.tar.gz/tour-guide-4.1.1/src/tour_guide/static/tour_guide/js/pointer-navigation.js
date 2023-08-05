(function() {

    window.tour_guide = window.tour_guide || {};
    const HUD = ((window.adede || {}).ui_components || {}).HUD;

    const PointerNavigation = function (element) {

        this.element_ = element;

        this.wasNavigating_ = false;

        this.startNavigating = this.startNavigating.bind(this);
        this.stopNavigating = this.stopNavigating.bind(this);

        this.updateHoverState = this.updateHoverState.bind(this);
        this.mouseEnteredDescendant = this.mouseEnteredDescendant.bind(this);
        this.mouseExitedDescendant = this.mouseExitedDescendant.bind(this);

        this.pointerAndHoverMediaQueryChanged = this.pointerAndHoverMediaQueryChanged.bind(this);

        this.element_.addEventListener("mouseover", this.mouseEnteredDescendant, false);
        this.element_.addEventListener("mouseout", this.mouseExitedDescendant, false);

        this.pointerAndHoverMediaQuery_ = window.matchMedia("(any-pointer: fine) and (any-hover: hover)");
        this.pointerAndHoverMediaQuery_.addListener(this.pointerAndHoverMediaQueryChanged);

        this.pointerAndHoverMediaQueryChanged(this.pointerAndHoverMediaQuery_);

        /*
        if( HUD != null ) {

            new HUD(this.element_);

            if( this.element_.dataset.initiatorActivationCondition ) {
                window.initiator.objects.initialisation.initialiseElementCondition(this.element_, "activation", this.element_.dataset.initiatorActivationCondition);
            }
        }
        */
    };

    PointerNavigation.prototype.pointerAndHoverMediaQueryChanged =
    function (event) {
    };

    PointerNavigation.prototype.startNavigating =
    function () {
        this.wasNavigating_ = true;

        const bodyElement = document.getElementsByTagName("body")[0];
        //const mainElement = document.getElementsByTagName("main")[0];
        //const screenElement = document.getElementsByClassName("site-navigation-screen")[0];

        window.setTimeout( () => {
            bodyElement.classList.add("navigating-site");
            //mainElement.classList.add("navigating-site");
            //screenElement.classList.add("effect-applied");
          }, 0);
    };

    PointerNavigation.prototype.stopNavigating =
    function () {
        this.wasNavigating_ = false;

        const bodyElement = document.getElementsByTagName("body")[0];
        //const mainElement = document.getElementsByTagName("main")[0];
        //const screenElement = document.getElementsByClassName("site-navigation-screen")[0];

        window.setTimeout( () => {
            bodyElement.classList.remove("navigating-site");
            //mainElement.classList.remove("navigating-site");
            //screenElement.classList.remove("effect-applied");
        }, 0);
    };

    PointerNavigation.prototype.updateHoverState =
    function (event) {
        // const rootMenuContainerElement = this.element_.getElementsByClassName("root-menu-container")[0];
        const isHovering = this.element_.matches(":hover");

        if( isHovering != this.wasNavigating_ ) {
            if( isHovering ) {
                this.startNavigating();
            } else {
                this.stopNavigating();
            }
        }
    };

    PointerNavigation.prototype.mouseEnteredDescendant =
    function (event) {
        event = event || window.event;
        this.updateHoverState(event);
    };

    PointerNavigation.prototype.mouseExitedDescendant =
    function (event) {
        event = event || window.event;
        this.updateHoverState(event);
    };

    window.tour_guide.PointerNavigation = PointerNavigation;

})();