
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
  <button class="new_button new_button_top" v-on:click="addFile($event)" v-if="filelist && filelist.length > 10">Nieuw</button>
  <ul v-for="item in filelist" class="filelist">
    <li v-if="item.children == null">
      <a :href="'/files/view/' + item.path" v-on:click="openFile(item, $event)" :title="item.title" >{{ item.title }}</a>
    </li>
    <li v-if="item.children" class="submenu submenu-closed" v-on:click="toggleVisible">
      {{ item.title }}
      <filelist
        v-bind:filelist="item.children"
        v-bind:container="container">
      </filelist>
    </li>
  </ul>
  <button v-on:click="addFile($event)" class="new_button new_button_bottom">Nieuw</button>
</div>
`,
  methods: {
    addFile: function(event) {
      event.stopPropagation();


      // HACK extract the base path from the first item in the file list.
      var path = this.filelist[0].path;
      if(path.match(/\//)) {
        path = path.replace(/\/[^\/]+$/, '/');
      } 
      else {
        path = '';
      }
      var fileName = window.prompt("Bestandsnaam", '*.md');
      if(! fileName) {
        return;
      }

      // Default to md files.
      if(! fileName.match(/\.[^\.]+$/)) {
        fileName = fileName + '.md';
      }

      var url = path + fileName;
      var title = fileName.replace(/\.[^\.]+$/, '');
      var openFileMethod = this.container.$options.methods.openFile;
      var container = this.container;
      var loadListMethod = this.container.$options.methods.loadList;

      $.ajax({
        url:    '/files/create',
        type:   'POST',
        data:   {
          'filepath' : url,
        },
        success:  function() {
          openFileMethod(title, url, container);
          loadListMethod(container);
        },
        error: function() {
          alert('Bestandsnaam ongeldig.');
        }
      });
    },
    openFile: function(file, event) {
      event.preventDefault();
      event.stopPropagation();
      this.container.$options.methods.openFile(file, this.container);
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
      'filepath'      : '',
    }, 
    components: {
      FileList,
    },
    mounted: function () { 
      this.loadList();
    }, 
    methods: {

      /**
       * Load the file list.
       * @param context optional: supply the variable to use as "this"
       */
      loadList: function(context) {
        var self = this;
        if(context) {
          self = context;
        }
        self.container = self; // Needed to load file data from a nested file list
        $.getJSON(apiURLs['filelist'], json => {
          self.filelist= json;
        })
      },

      /**
       * Read data for an item into filecontents, but only if it's viewable
       * (viewable means: markdown, html or text).
       * @param item the file item to display.
       * @param context the context to use, ie this object. The child needs to
       * pass its parent to us this way because otherwise we can't find our
       * own object.
       */
      openFile: function(item, context) {
        var url = item.path;
        var title = item.title;
        var type = item.type;

        console.log('Asked to open file ' + title + ' of type ' + type +  ' at url ' + url);
        // Not a type we can show. Force download.
        if (type != 'md' && type != 'html' && type != 'txt') {
          document.location = '/files/view/' + url;
        }
        // It's a type we can show. Show it.
        var self = context;
        $.getJSON('/files/view/' + url, json => {
          if(! 'content' in json || ! 'type' in json) {
            console.log('no content or type in ', json);
            return;
          }
          self.filecontents = json.contents;
          self.filetype = json.type;
          self.filetitle = title;
          self.filepath = url;
        });
      },

      // Debounced version
      autosave: _.debounce(() => {
        filelist.saveFile();
      }, 1000),


      // Non-debounced version
      update: function(event) {
        event.preventDefault();
        event.stopPropagation();
        filelist.saveFile();
      },

      
      // The method that does the saving.
      saveFile() {
        self = this;
        $.ajax({
          url: '/files/save/' + self.filepath,
          type: 'PUT',
          // TODO failure melden
          data: {'filecontents': self.filecontents},
        });
        
      },

    },
  });


})


