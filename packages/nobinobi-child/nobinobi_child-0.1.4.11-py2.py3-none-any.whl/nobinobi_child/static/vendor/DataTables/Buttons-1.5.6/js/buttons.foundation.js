/*
 * Copyright (C) 2020 <Florian Alu - Prolibre - https://prolibre.com
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as
 * published by the Free Software Foundation, either version 3 of the
 * License, or (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
 */

/*! Foundation integration for DataTables' Buttons
 * ©2016 SpryMedia Ltd - datatables.net/license
 */

(function( factory ){
	if ( typeof define === 'function' && define.amd ) {
		// AMD
		define( ['jquery', 'datatables.net-zf', 'datatables.net-buttons'], function ( $ ) {
			return factory( $, window, document );
		} );
	}
	else if ( typeof exports === 'object' ) {
		// CommonJS
		module.exports = function (root, $) {
			if ( ! root ) {
				root = window;
			}

			if ( ! $ || ! $.fn.dataTable ) {
				$ = require('datatables.net-zf')(root, $).$;
			}

			if ( ! $.fn.dataTable.Buttons ) {
				require('datatables.net-buttons')(root, $);
			}

			return factory( $, root, root.document );
		};
	}
	else {
		// Browser
		factory( jQuery, window, document );
	}
}(function( $, window, document, undefined ) {
'use strict';
var DataTable = $.fn.dataTable;


// F6 has different requirements for the dropdown button set. We can use the
// Foundation version found by DataTables in order to support both F5 and F6 in
// the same file, but not that this requires DataTables 1.10.11+ for F6 support.
var collection = DataTable.ext.foundationVersion === 6 ?
	{
		tag: 'div',
		className: 'dt-button-collection dropdown-pane is-open button-group stacked'
	} :
	{
		tag: 'ul',
		className: 'dt-button-collection f-dropdown open dropdown-pane is-open',
		button: {
			tag: 'li',
			className: 'small',
			active: 'active',
			disabled: 'disabled'
		},
		buttonLiner: {
			tag: 'a'
		}
	};

$.extend( true, DataTable.Buttons.defaults, {
	dom: {
		container: {
			tag: 'div',
			className: 'dt-buttons button-group'
		},
		buttonContainer: {
			tag: null,
			className: ''
		},
		button: {
			tag: 'a',
			className: 'button small',
			active: 'secondary'
		},
		buttonLiner: {
			tag: null
		},
		collection: collection
	}
} );


DataTable.ext.buttons.collection.className = 'buttons-collection dropdown';


return DataTable.Buttons;
}));
