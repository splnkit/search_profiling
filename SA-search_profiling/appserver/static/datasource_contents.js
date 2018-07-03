var initHash = location.hash;
require([
    'jquery',
    'underscore',
    'splunkjs/mvc/simplexml/controller',
    'splunk.util',
    'backbone',
    'collections/services/data/ui/Views',
    'models/services/data/ui/View',
    '../app/SA-search_profiling/components/kvstore_backbone/kvstore',
    'bootstrap.affix',
    'bootstrap.scrollspy',
], function($, _, DashboardController, SplunkUtil, Backbone, ViewsCollection, ViewModel, KVStore) {
    var TAGS = {
        'extension': {
            label: _('Extension').t(),
            tooltip: _('Uses external JS/CSS').t()
        },
        'new': {
            label: _('New Example').t(),
            tooltip: ''
        },
        'updated': {
            label: _('Updated Example').t(),
            tooltip: ''
        },
        'app_deps': {
            label: _('App Dependency').t(),
            tooltip: _('Requires installing other apps').t()
        }
    };

    var UseCaseModel = KVStore.Model.extend({
        collectionName: 'data_sources'
    });

    var UseCaseCollection = KVStore.Collection.extend({
        collectionName: 'data_sources',
        model: UseCaseModel
    });

    var HIDE_MISSING_VIEWS = false;
    
    var DashboardsCollection = ViewsCollection.extend({
            model: ViewModel,
            initialize: function() {
                ViewsCollection.prototype.initialize.apply(this, arguments);
            },
            sync: function(method, collection, options) {
                options = options || {};
                options.data = options.data || {};
                var baseSearch = '(isDashboard=1 AND isVisible=1)';
                if(!options.data.search){
                    options.data.search = baseSearch;
                } else {
                    options.data.search = ['(',baseSearch,' AND ', options.data.search,')'].join('');
                }
                return ViewsCollection.prototype.sync.call(this, method, collection, options);
            }
        });

    DashboardController.onReady(function() {

        // foogendoogen.fry();

        console.log("Ready!!!")

        DashboardController.onViewModelLoad(function() {
            var app = DashboardController.model.app.get('app');
            var view = DashboardController.model.view;
            var dashboards = new DashboardsCollection();
            var dashboardsLoaded = dashboards.fetch({ data : { app: app, owner: '-', count: 0 } });
            // var exampleInfoCollection = new Backbone.Collection();
            // var exampleInfoLoaded = exampleInfoCollection.fetch({
            //     url: SplunkUtil.make_url('/static/app/' + app +'/exampleInfo.json'),
            //     cache: true
            // });
            var exampleInfoCollection = new UseCaseCollection();
            var exampleInfoLoaded = exampleInfoCollection.fetch();

            $.when(exampleInfoLoaded, dashboardsLoaded).then(function(){
                var categories = _.uniq(_.flatten(exampleInfoCollection.pluck('category')));
                var $nav = $('<ul class="nav nav-list"></ul>').data('offset-top', "50");
                var $contents = $('<div class="example-contents"></div>');
                _.each(categories, function(category){
                    var categoryFiltered = exampleInfoCollection.filter(function(exampleInfo) {
                        return _.flatten([exampleInfo.get("category")]).indexOf(category) > -1;
                    });
                    $nav.append($('<li></li>').append($('<a ></a>').attr('href', '#' + category.replace(/ /g,"_")).text(category)));
                    var categoryInfoCollection = new Backbone.Collection(categoryFiltered);
                    var $category= $('<section></section>').attr('id', category.replace(/ /g,"_"));
                    $category.append($("<h2></h2>").text(category));
                    var $categoryContents = $('<div class=""></div>').appendTo($category);
                    categoryInfoCollection.each(function(exampleInfo){
                        var id = exampleInfo.get('title');
                        var $example = $('<a class="example"></a>').attr('href', "datasources?form.datasource="+id);
                        var view = dashboards.find(function(m){ return m.entry.get('name') === id; });
                        if(!view) {
                            if(HIDE_MISSING_VIEWS) { return; }
                            $example.addClass('missing').attr("title", "Example view is not available!");
                        }
                        var label = exampleInfo.get('title') || (view && view.entry.content.get('label') || id);
                        var $exampleTitle = $('<h3></h3>').text(label);
                        var $exampleImg = $('<img />').attr('src', SplunkUtil.make_url('/static/app/' + app +'/icons/' + (exampleInfo.get('description-icon') || exampleInfo.get('id') + ".png")));
                        var $exampleDescription = $('<p></p>').html(exampleInfo.get('description'));
                        var $exampleContent = $('<div class="content"></div>').append($exampleTitle).append($exampleDescription);
                        var $tags =  $('<div class="tags"></div>').appendTo($exampleContent);
                        _.each(exampleInfo.get('tags'), function(tag){
                            var tooltip = TAGS[tag].tooltip;
                            var label = TAGS[tag].label;
                            $tags.append($('<span class="label"></span>').addClass(tag).attr('title', tooltip).tooltip().text(label));
                        });
                        var $versions =  $('<div class="versions"></div>').appendTo($exampleContent);
                        _.each(exampleInfo.get('partial_versions'), function(version){
                            $versions.append($('<span class="label"></span>').addClass(version).attr('title', 'Partially Supported Version').tooltip().text(version));
                        });
                        // _.each(exampleInfo.get('versions'), function(version){
                        //     $versions.append($('<span class="label full_support"></span>').addClass(version).attr('title', 'Version').tooltip().text(version));
                        // });
                        $versions.append($('<span class="label full_support"></span>').addClass(exampleInfo.get('value')).attr('title', 'Value').tooltip().text(exampleInfo.get('value')));
                        $example.append($exampleContent); //.append($exampleImg)
                        $categoryContents.append($example);
                    });
                    $contents.append($category);
                });
                $('.dashboard-body').append($('<div class="row contents-body"></div>').append($('<div class="nav-bar-slide"></div>').append($nav)).append($contents));
                $nav.affix({
                    offset: { top: $nav.offset().top }
                });
                $('body').scrollspy();
                if (initHash) {
                    setTimeout(function() {
                        document.body.scrollTop = $(initHash).offset().top;
                    }, 100);
                }
            });

        });

    });

});
