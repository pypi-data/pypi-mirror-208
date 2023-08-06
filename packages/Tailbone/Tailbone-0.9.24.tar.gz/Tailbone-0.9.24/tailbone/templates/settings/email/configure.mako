## -*- coding: utf-8; -*-
<%inherit file="/configure.mako" />

<%def name="form_content()">

  <h3 class="block is-size-3">Sending</h3>
  <div class="block" style="padding-left: 2rem;">

    <b-field>
      <b-checkbox name="rattail.mail.record_attempts"
                  v-model="simpleSettings['rattail.mail.record_attempts']"
                  native-value="true"
                  @input="settingsNeedSaved = true">
        Make record of all attempts to send email
      </b-checkbox>
    </b-field>

    <b-field>
      <b-checkbox name="rattail.mail.send_email_on_failure"
                  v-model="simpleSettings['rattail.mail.send_email_on_failure']"
                  native-value="true"
                  @input="settingsNeedSaved = true">
        When sending an email fails, send another to report the failure
      </b-checkbox>
    </b-field>

  </div>

  % if request.has_perm('errors.bogus'):
      <h3 class="block is-size-3">Testing</h3>
      <div class="block" style="padding-left: 2rem;">

        <b-field grouped>
          <p class="control">
            You can raise a "bogus" error to test if/how it generates email:
          </p>
          <b-button type="is-primary"
                    @click="raiseBogusError()"
                    :disabled="raisingBogusError">
            {{ raisingBogusError ? "Working, please wait..." : "Raise Bogus Error" }}
          </b-button>
        </b-field>

      </div>
      </h3>
  % endif
</%def>

<%def name="modify_this_page_vars()">
  ${parent.modify_this_page_vars()}
  % if request.has_perm('errors.bogus'):
      <script type="text/javascript">

        ThisPageData.raisingBogusError = false

        ThisPage.methods.raiseBogusError = function() {
            this.raisingBogusError = true

            let url = '${url('bogus_error')}'
            this.$http.get(url).then(response => {
                this.$buefy.toast.open({
                    message: "Ironically, response was 200 which means we failed to raise an error!\n\nPlease investigate!",
                    type: 'is-danger',
                    duration: 5000, // 5 seconds
                })
                this.raisingBogusError = false
            }, response => {
                this.$buefy.toast.open({
                    message: "Error was raised; please check your email and/or logs.",
                    type: 'is-success',
                    duration: 4000, // 4 seconds
                })
                this.raisingBogusError = false
            })
        }

      </script>
  % endif
</%def>


${parent.body()}
