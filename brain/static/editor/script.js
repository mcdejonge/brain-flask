
//import FileList from './FileList.vue'
//
//
Vue.component('filelist',  {
  props: ['filelist'],
  template:
`
<div>
<ul v-for="item in filelist">
        <li v-if="item.children == null">
          <a :href="'/files/view/' + item.path" v-on:click="loadFile">{{ item.title }}</a>
        </li>
        <li v-if="item.children">
          {{ item.title }}
          <filelist
            v-bind:filelist="item.children">
          </filelist>
        </li>
      
    </ul>
  </div>
`
})
window.addEventListener('load', function () {

  var apiURLs = {
    'filelist' : '/files',
    'file' : '/file/view',
  };

  var filelist = new Vue({ 
    el: '#wrapper', 
    data: { 
      'filelist' : null
    }, 
    components: {
      FileList,
    },
    mounted: function () { 
      var self = this;
      $.getJSON(apiURLs['filelist'], json => {
        self.filelist= json;
      })
     }, 
    methods: {
      loadFile: function(event) {
        console.log('nou daar gaan we');
      },
    },
  });


})


