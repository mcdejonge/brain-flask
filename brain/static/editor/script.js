
Vue.component('filelist',  {
  // The parent needs to pass itself because we're calling ourselves
  // recursively and we need to get to to top level object.
  props: ['filelist', 'container'],
  data: function() {
      return {
      }
  },
  template:
`
<div>
<ul v-for="item in filelist" class="filelist">
        <li v-if="item.children == null">
          <a :href="'/files/view/' + item.path" v-on:click="openFile(item.title, item.path, $event)">{{ item.title }}</a>
        </li>
        <li v-if="item.children" class="submenu submenu-closed" v-on:click="toggleVisible">
          {{ item.title }}
          <filelist
            v-bind:filelist="item.children"
            v-bind:container="container">
          </filelist>
        </li>
      
    </ul>
  </div>
`,
  methods: {
    openFile: function(title, url, event) {
      event.preventDefault();
      event.stopPropagation();
      this.container.$options.methods.openFile(title, url, this.container);
    },
    toggleVisible(event) {
      event.target.classList.toggle('submenu-closed')
      event.stopPropagation();
      event.preventDefault();
    }
  }
})
window.addEventListener('load', function () {

  var apiURLs = {
    'filelist' : '/files',
    'file' : '/file/view',
  };

  var filelist = new Vue({ 
    el: '#wrapper', 
    data: { 
      'filelist'      : null,
      'filecontents'  : '',
      'filetype'      : 'txt',
      'filetitle'     : '',
      'container'     : null,
    }, 
    components: {
      FileList,
    },
    mounted: function () { 
      var self = this;
      self.container = self; // Needed to load file data from a nested file list
      $.getJSON(apiURLs['filelist'], json => {
        self.filelist= json;
      })
     }, 
    methods: {
      /**
       * Read data from an URL into filecontents.
       * @param title the title to display
       * @param url the url to load the data from
       * @param context the context to use, ie this object. The child needs to
       * pass its parent to us this way because otherwise we can't find our
       * own object.
       */
      openFile: function(title, url, context) {
        var self = context;
        $.getJSON('/files/view/' + url, json => {
          if(! 'content' in json || ! 'type' in json) {
            console.log('no content or type in ', json);
            return;
          }
          self.filecontents = json.contents;
          self.filetype = json.type;
          self.filetitle = title;
        });
      },

      update: function(event) {
        console.log('here updating happens');
      },

    },
  });


})


