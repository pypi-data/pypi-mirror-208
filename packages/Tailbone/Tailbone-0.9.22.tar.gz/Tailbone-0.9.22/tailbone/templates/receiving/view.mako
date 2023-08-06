## -*- coding: utf-8; -*-
<%inherit file="/batch/view.mako" />

<%def name="extra_styles()">
  ${parent.extra_styles()}
  <style type="text/css">
    % if allow_edit_catalog_unit_cost:
        td.c_catalog_unit_cost {
            cursor: pointer;
            background-color: #fcc;
        }
        tr.catalog_cost_confirmed td.c_catalog_unit_cost {
            background-color: #cfc;
        }
    % endif
    % if allow_edit_invoice_unit_cost:
        td.c_invoice_unit_cost {
            cursor: pointer;
            background-color: #fcc;
        }
        tr.invoice_cost_confirmed td.c_invoice_unit_cost {
            background-color: #cfc;
        }
    % endif
  </style>
</%def>

<%def name="render_po_vs_invoice_helper()">
  % if master.handler.has_purchase_order(batch) and master.handler.has_invoice_file(batch):
      <div class="object-helper">
        <h3>PO vs. Invoice</h3>
        <div class="object-helper-content">
          ${po_vs_invoice_breakdown_grid}
        </div>
      </div>
  % endif
</%def>

<%def name="render_auto_receive_helper()">
  % if master.has_perm('auto_receive') and master.can_auto_receive(batch):

      <div class="object-helper">
        <h3>Tools</h3>
        <div class="object-helper-content">
          <b-button type="is-primary"
                    @click="autoReceiveShowDialog = true"
                    icon-pack="fas"
                    icon-left="check">
            Auto-Receive All Items
          </b-button>
        </div>
      </div>

      <b-modal has-modal-card
               :active.sync="autoReceiveShowDialog">
        <div class="modal-card">

          <header class="modal-card-head">
            <p class="modal-card-title">Auto-Receive All Items</p>
          </header>

          <section class="modal-card-body">
            <p class="block">
              You can automatically set the "received" quantity to
              match the "shipped" quantity for all items, based on
              the invoice.
            </p>
            <p class="block">
              Would you like to do so?
            </p>
          </section>

          <footer class="modal-card-foot">
            <b-button @click="autoReceiveShowDialog = false">
              Cancel
            </b-button>
            ${h.form(url('{}.auto_receive'.format(route_prefix), uuid=batch.uuid), **{'@submit': 'autoReceiveSubmitting = true'})}
            ${h.csrf_token(request)}
            <b-button type="is-primary"
                      native-type="submit"
                      :disabled="autoReceiveSubmitting"
                      icon-pack="fas"
                      icon-left="check">
              {{ autoReceiveSubmitting ? "Working, please wait..." : "Auto-Receive All Items" }}
            </b-button>
            ${h.end_form()}
          </footer>
        </div>
      </b-modal>
  % endif
</%def>

<%def name="render_this_page_template()">
  ${parent.render_this_page_template()}

  % if allow_edit_catalog_unit_cost or allow_edit_invoice_unit_cost:
      <script type="text/x-template" id="receiving-cost-editor-template">
        <div>
          <span v-show="!editing">
            {{ value }}
          </span>
          <b-input v-model="inputValue"
                   ref="input"
                   v-show="editing"
                   @keydown.native="inputKeyDown"
                   @blur="inputBlur">
          </b-input>
        </div>
      </script>
  % endif
</%def>

<%def name="object_helpers()">
  ${self.render_status_breakdown()}
  ${self.render_po_vs_invoice_helper()}
  ${self.render_execute_helper()}
  ${self.render_auto_receive_helper()}
</%def>

<%def name="modify_this_page_vars()">
  ${parent.modify_this_page_vars()}
  <script type="text/javascript">

    ThisPageData.autoReceiveShowDialog = false
    ThisPageData.autoReceiveSubmitting = false

    % if po_vs_invoice_breakdown_data is not Undefined:
        ThisPageData.poVsInvoiceBreakdownData = ${json.dumps(po_vs_invoice_breakdown_data)|n}

        ThisPage.methods.autoFilterPoVsInvoice = function(row) {
            let filters = []
            if (row.key == 'both') {
                filters = [
                    {key: 'po_line_number',
                     verb: 'is_not_null'},
                    {key: 'invoice_line_number',
                     verb: 'is_not_null'},
                ]
            } else if (row.key == 'po_not_invoice') {
                filters = [
                    {key: 'po_line_number',
                     verb: 'is_not_null'},
                    {key: 'invoice_line_number',
                     verb: 'is_null'},
                ]
            } else if (row.key == 'invoice_not_po') {
                filters = [
                    {key: 'po_line_number',
                     verb: 'is_null'},
                    {key: 'invoice_line_number',
                     verb: 'is_not_null'},
                ]
            } else if (row.key == 'neither') {
                filters = [
                    {key: 'po_line_number',
                     verb: 'is_null'},
                    {key: 'invoice_line_number',
                     verb: 'is_null'},
                ]
            }

            if (!filters.length) {
                return
            }

            this.$refs.rowGrid.setFilters(filters)
            document.getElementById('rowGrid').scrollIntoView({
                behavior: 'smooth',
            })
        }

    % endif

    % if allow_edit_catalog_unit_cost or allow_edit_invoice_unit_cost:

        let ReceivingCostEditor = {
            template: '#receiving-cost-editor-template',
            props: {
                row: Object,
                'field': String,
                value: String,
            },
            data() {
                return {
                    inputValue: this.value,
                    editing: false,
                }
            },
            methods: {

                startEdit() {
                    this.inputValue = this.value
                    this.editing = true
                    this.$nextTick(() => {
                        this.$refs.input.focus()
                    })
                },

                inputKeyDown(event) {

                    // when user presses Enter while editing cost value, submit
                    // value to server for immediate persistence
                    if (event.which == 13) {
                        this.submitEdit()

                    // when user presses Escape, cancel the edit
                    } else if (event.which == 27) {
                        this.cancelEdit()
                    }
                },

                inputBlur(event) {
                    // always assume user meant to cancel
                    this.cancelEdit()
                },

                cancelEdit() {
                    // reset input to discard any user entry
                    this.inputValue = this.value
                    this.editing = false
                    this.$emit('cancel-edit')
                },

                submitEdit() {
                    let url = '${url('{}.update_row_cost'.format(route_prefix), uuid=batch.uuid)}'

                    // TODO: should get csrf token from parent component?
                    let csrftoken = ${json.dumps(request.session.get_csrf_token() or request.session.new_csrf_token())|n}
                    let headers = {'${csrf_header_name}': csrftoken}

                    let params = {
                        row_uuid: this.$props.row.uuid,
                    }
                    params[this.$props.field] = this.inputValue

                    this.$http.post(url, params, {headers: headers}).then(response => {
                        if (!response.data.error) {

                            // let parent know cost value has changed
                            // (this in turn will update data in *this*
                            // component, and display will refresh)
                            this.$emit('input', response.data.row[this.$props.field],
                                       this.$props.row._index)

                            // and hide the input box
                            this.editing = false

                        } else {
                            this.$buefy.toast.open({
                                message: "Submit failed:  " + response.data.error,
                                type: 'is-warning',
                                duration: 4000, // 4 seconds
                            })
                        }

                    }, response => {
                        this.$buefy.toast.open({
                            message: "Submit failed:  (unknown error)",
                            type: 'is-warning',
                            duration: 4000, // 4 seconds
                        })
                    })
                },
            },
        }

        Vue.component('receiving-cost-editor', ReceivingCostEditor)

    % endif

    % if allow_edit_catalog_unit_cost:

        ${rows_grid.component_studly}.methods.catalogUnitCostClicked = function(row) {

            // start edit for clicked cell
            this.$refs['catalogUnitCost_' + row.uuid].startEdit()
        }

        ${rows_grid.component_studly}.methods.catalogCostConfirmed = function(amount, index) {

            // update display to indicate cost was confirmed
            this.addRowClass(index, 'catalog_cost_confirmed')

            // start editing next row, unless there are no more
            let nextRow = index + 1
            if (this.data.length > nextRow) {
                nextRow = this.data[nextRow]
                this.$refs['catalogUnitCost_' + nextRow.uuid].startEdit()
            }
        }

    % endif

    % if allow_edit_invoice_unit_cost:

        ${rows_grid.component_studly}.methods.invoiceUnitCostClicked = function(row) {

            // start edit for clicked cell
            this.$refs['invoiceUnitCost_' + row.uuid].startEdit()
        }

        ${rows_grid.component_studly}.methods.invoiceCostConfirmed = function(amount, index) {

            // update display to indicate cost was confirmed
            this.addRowClass(index, 'invoice_cost_confirmed')

            // start editing next row, unless there are no more
            let nextRow = index + 1
            if (this.data.length > nextRow) {
                nextRow = this.data[nextRow]
                this.$refs['invoiceUnitCost_' + nextRow.uuid].startEdit()
            }
        }

    % endif

  </script>
</%def>


${parent.body()}
