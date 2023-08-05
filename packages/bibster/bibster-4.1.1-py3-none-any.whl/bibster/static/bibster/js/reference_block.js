(function(window) {

        const SwitchBlock = window.wagtail_switch_block.SwitchBlock;
        const SwitchBlockDefinition = window.wagtail_switch_block.SwitchBlockDefinition;
        const SwitchBlockValidationError = window.wagtail_switch_block.SwitchBlockValidationError;

        const indexInParent = function (parent, child) {
            var result = 0;
            for( var element of parent.children ) {
                if( element === child ) {
                    return result;
                }

                result += 1;
            }

            return -1;
        };

        const PROLOGUE = '<div style="padding-top: .5em; padding-bottom: 1.2em;">'
        + '<textarea id="__PREFIX__-lookup-textarea" placeholder="Enter DOI or Bibliographic Information here" style="margin-top: .5em; margin-bottom: 1.2em;"></textarea>'
        + '<button id="__PREFIX__-lookup-button" class="button" type="button">Look up</button>'
        + '</div>';

        class ReferenceBlock extends SwitchBlock {
          constructor(blockDef, placeholder, prefix, initialState, initialError) {
            var placeholderParent = placeholder.parentElement;
            var childIndex = indexInParent(placeholderParent, placeholder);

            super(blockDef, placeholder, prefix, initialState, initialError);

            if( blockDef.createEndpoint ) {
                placeholder = placeholderParent.children[childIndex];
                placeholder.insertAdjacentHTML("beforebegin", PROLOGUE.replace(/__PREFIX__/g, prefix));
                new window.bibster.LookupEndpoint(prefix, blockDef.targetURL, placeholderParent, childIndex + 1);
            }
          }
        };


        class ReferenceBlockDefinition extends SwitchBlockDefinition {
          constructor(name, childBlockDefs, meta, targetURL) {
            super(name, childBlockDefs, meta);
            this.targetURL = targetURL;
            this.createEndpoint = true;
          }

          render(placeholder, prefix, initialState, initialError) {
            return new ReferenceBlock(
              this,
              placeholder,
              prefix,
              initialState,
              initialError,
            );
          }
        };

        if( window.bibster == null ) {
            window.bibster = {};
        }

        window.bibster.ReferenceBlock = ReferenceBlock;
        window.bibster.ReferenceBlockDefinition = ReferenceBlockDefinition;
        window.bibster.ReferenceBlockValidationError = SwitchBlockValidationError;

        window.telepath.register(
            'bibster.ReferenceBlock',
            ReferenceBlockDefinition);

        window.telepath.register(
          'bibster.ReferenceBlockValidationError',
          SwitchBlockValidationError
        );

})( typeof window !== "undefined" ? window: this);

