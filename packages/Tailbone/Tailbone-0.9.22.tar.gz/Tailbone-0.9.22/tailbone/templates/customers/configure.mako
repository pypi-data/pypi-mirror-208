## -*- coding: utf-8; -*-
<%inherit file="/configure.mako" />

<%def name="form_content()">

  <h3 class="block is-size-3">General</h3>
  <div class="block" style="padding-left: 2rem;">

    <b-field message="If not set, customer chooser is an autocomplete field.">
      <b-checkbox name="rattail.customers.choice_uses_dropdown"
                  v-model="simpleSettings['rattail.customers.choice_uses_dropdown']"
                  native-value="true"
                  @input="settingsNeedSaved = true">
        Show customer chooser as dropdown (select) element
      </b-checkbox>
    </b-field>

  </div>

  <h3 class="block is-size-3">POS</h3>
  <div class="block" style="padding-left: 2rem;">

    <b-field>
      <b-checkbox name="rattail.customers.active_in_pos"
                  v-model="simpleSettings['rattail.customers.active_in_pos']"
                  native-value="true"
                  @input="settingsNeedSaved = true">
        Expose/track the "Active in POS" flag for customers.
      </b-checkbox>
    </b-field>

  </div>

</%def>


${parent.body()}
