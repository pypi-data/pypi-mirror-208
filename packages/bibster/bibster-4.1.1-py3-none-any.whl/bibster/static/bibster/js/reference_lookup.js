(function () {

    const LookupEndpoint = function(prefix, target_url, placeholderParent, childIndex) {

        this.prefix_ = prefix;
        this.target_url_ = target_url;
        this.placeholderParent_ = placeholderParent;
        this.childIndex_ = childIndex;

        this.button_clicked = this.button_clicked.bind(this);
        this.result_received = this.result_received.bind(this);
        this.set_form_fields = this.set_form_fields.bind(this);

        const buttonElement = document.getElementById(this.prefix_ + "-lookup-button");
        buttonElement.addEventListener("click", this.button_clicked, false);
    };

    LookupEndpoint.prototype.button_clicked = function (event) {

        const textElement = document.getElementById(this.prefix_ + "-lookup-textarea");
        const queryParam = encodeURIComponent(textElement.value);

        const request = new XMLHttpRequest();

        request.open("GET", this.target_url_ + "?query=" + queryParam, true);
        request.responseType = "json";
        request.onload = this.result_received;
        request.send();
    };

    LookupEndpoint.prototype.result_received = function (event) {
        const request = event.target;

        if( request.readyState == 4 ) { //LOADED
            if( request.response ) {
                this.set_form_fields(request.response);
            }
        }
    };


    LookupEndpoint.prototype.set_form_fields = function (lookup_result) {

        if( lookup_result.reference_type ) {

            const input_element = document.getElementById(this.prefix_ + "-__type__");
            input_element.value = lookup_result.reference_type;
            input_element.dispatchEvent(new Event("change"));
        }

        const blockDef = window.telepath.unpack(lookup_result.blockDef);
        const blockErrors = window.telepath.unpack(lookup_result.blockErrors);

        // blockDef is a ReferenceBlockDefinition, make sure we do not recreate this endpoint:
        blockDef.createEndpoint = false;

        var placeholder = this.placeholderParent_.children[this.childIndex_];
        const blockInstance = blockDef.render(placeholder, this.prefix_, lookup_result.blockValue, null);

        if( blockErrors != null) {
            if( blockErrors.length != undefined && blockErrors.length != 0 ) {
                blockInstance.setError(blockErrors);
            }
        }

        /*
        for (let assignment of lookup_result.assignments) {

            const key = assignment[0];
            const value = assignment[1];
            const input_element_id = this.prefix_ + "-" + key;
            const input_element = document.getElementById(input_element_id);

            if( input_element == null ) {
                if( LookupEndpoint.is_stream_field_array(value) ) {
                    LookupEndpoint.update_stream_field(input_element_id, value);
                }

                continue;
            }

            input_element.value = value;
        }
        */
    };


    LookupEndpoint.is_stream_field_array = function (value) {

        if( !Array.isArray(value) ) return false;

        for (let element of value) {

            if( !Array.isArray(element) ) return false;

            var type_fields = 0;
            var value_fields = 0;

            for (let part of element) {

                if( !Array.isArray(part) ) return false;
                if( part.length != 2 ) return false;

                type_fields += part[0] == "type" ? 1 : 0;
                value_fields += part[0].startsWith("value-") ? 1 : 0;
            }

            if( type_fields != 1 ) return false;
            if( value_fields == 0 ) return false;
        }

        return true;
    };

    LookupEndpoint.get_stream_field_value_type = function (value) {

        for (let part of value) {

            if( part[0] != "type" ) continue;

            return part[1];
        }

        return null;
    };

    LookupEndpoint.click_append_new_sequence_member = function (id, sequence_members, block_identifier) {

        var menu_id = "";

        if( sequence_members.length == 0 ) {
            menu_id = id + "-prependmenu";
        } else {
            const last_member = sequence_members[sequence_members.length - 1];
            menu_id = last_member.id.replace( /-container/, "") + "-appendmenu";
        }

        const menu_element = document.getElementById(menu_id);
        const menu_is_closed = menu_element.classList.contains("stream-menu-closed");

        if( menu_is_closed ) {
            menu_element.classList.remove("stream-menu-closed");
        }

        const add_button = menu_element.getElementsByClassName("action-add-block" + "-" + block_identifier)[0];

        add_button.click();
    };


    LookupEndpoint.update_stream_field = function (id, stream_field_array) {

        const list_id = id + "-list";
        const list_element = document.getElementById(list_id);
        const list_items = list_element.getElementsByClassName("sequence-member");

        for (let i of Array(stream_field_array.length).keys()) {
            let stream_element = stream_field_array[i];
            let stream_element_type = LookupEndpoint.get_stream_field_value_type(stream_element);
            LookupEndpoint.click_append_new_sequence_member(id, list_items, stream_element_type);
        }

        const sequence_member_ids = [];

        for (let list_item of list_items) {
            const indicator_id = list_item.id.replace( /-container/, "-deleted");
            const indicator = document.getElementById(indicator_id);
            const is_deleted = indicator.value == "1";

            if( !is_deleted ) {
                sequence_member_ids.push(list_item.id.replace( /-container/, ""));
            }
        }

        for (let i of Array(stream_field_array.length).keys()) {
            let stream_element = stream_field_array[i];
            let stream_element_id = sequence_member_ids[i];

            for (let assignment of stream_element) {

                if( !assignment[0].startsWith("value-") ) continue;

                let value_id = stream_element_id + "-" + assignment[0];
                let value_element = document.getElementById(value_id);

                if( value_element == null)  continue;

                value_element.value = assignment[1];
            }
        }
    };

    if( window.bibster == null ) {
        window.bibster = {};
    }

    window.bibster.LookupEndpoint = LookupEndpoint;
})();