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
      var container = this.container;
      var loadListMethod = this.container.$options.methods.loadList;

      $.ajax({
        url:    '/files/create',
        type:   'POST',
        data:   {
          'filepath' : url,
        },
        success: function() {
          // Nasty. In the redirect the fact that we want json data gets lost.
          // So instead we have to manually call the view url and  load the
          // data.
          $.getJSON('/files/view/' + url, json => {

            // TODO duplicate code
            container.filecontents = json.contents;
            container.filetype = json.type;
            container.filetitle = title;
            container.filepath = url;

            loadListMethod(container);
          });
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
      'filelist'        : null,
      'filecontents'    : '',
      'filetype'        : 'txt',
      'filetitle'       : '',
      'container'       : null,
      'filepath'        : '',
      // HACK to make updating the filetitle work using contenteditable,
      // we store the element its displayed in. Then, when saving
      // we fetch the current value and update the file title
      'ftcontainer'     : null,
      // To force saving before opening a new file AND to avoid saving an
      // incorrect file.
      // Note this only works well enough to avoid saving the new file.
      'wantsSave'       : false,
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

        // Not a type we can show. Force download.
        if (type != 'md' && type != 'html' && type != 'txt') {
          document.location = '/files/view/' + url;
        }
        // It's a type we can show. Show it.
        var self = context;
        if(self.wantsSave) {
          this.saveFile();
          self.wantsSave = false;
        }
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

      /**
       * Save title of current file.
       */
      // Update the current in memory title.
      updatetitle: function(event) {
        this.ftcontainer = event.target
        this.saveTitleDebounced();
      },
      // Debounced version of the save method
      saveTitleDebounced : _.debounce(() => {
          filelist.saveTitle();
        }, 500),

      // The method that does the saving.
      saveTitle: function() {
        var self = this;
        var container = self.ftcontainer;
        var newtitle = container.innerText.trim();
        if (! newtitle)  {
          return;
        }
        $.ajax({
          url: '/files/rename/' + self.filepath,
          type: 'POST',
          data: {'newtitle' : newtitle},
          error: function(response) {
            console.log('Unable to rename file');
            container.innerText = self.filetitle;
          },
          success: function(response) {
            self.filetitle = newtitle;
            self.filepath = response;
            self.loadList();
          }
        });
      },


      /**
       * Save contents of current file.
       */
      // Set the wantsSave flag and trigger the debounced method.
      autosave: function() {
        if(this.wantsSave) {
          return;
        }
        this.wantsSave = true;
        this.autosaveDebounced();
      },

      // Debounced version
      autosaveDebounced: _.debounce(() => {
        filelist.saveFile();
      }, 1000),

      // Non-debounced version
      update: function(event) {
        event.preventDefault();
        event.stopPropagation();
        self.wantsSave = true;
        filelist.saveFile();
      },

      // The method that does the saving.
      saveFile() {
        self = this;
        if(! self.wantsSave) {
          return;
        }
        self.wantsSave = false;

        $.ajax({
          url: '/files/save/' + self.filepath,
          type: 'PUT',
          // TODO failure melden
          data: {'filecontents': self.filecontents},
        });
        
      },

      /**
       * Helper method for unloading the current file from memory.
       */
      unloadFile: function() {
        this.filecontents = '';
        this.filetype = 'txt';
        this.filetitle = '';
        this.filepath = '';
        this.wantsSave = false;
      },

      /**
       * Delete.
       */
      deletefile: function(event) {
        if(! confirm('Zeker weten?')) {
          return;
        }
        var filepath = this.filepath;
        this.unloadFile();

        var container = this.container;
        var loadListMethod = this.container.$options.methods.loadList;

        $.ajax({
          url: '/files/delete/' + filepath,
          type: 'DELETE',
          success:  function() {
            loadListMethod(container);
          },

        })
      },

    },
  });


})


