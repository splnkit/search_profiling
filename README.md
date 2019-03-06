App For Search Profiling
========================

Team: Nate Kwong, Thomas Przelomiec, Nik Macroglou, Gary Burgett

For Questions email: <search-insights@splunk.com> 

Helping Splunk owners understand what data they have and how it's being used.

Splunk makes it extremely easy to use, explore and gain value from machine data and also
makes it easy to track what data is being collected, and how much. However its internal 
logging does not make it easy to see how each data source is being used, by whom, and for
what purposes. These are the questions that this app seeks to help answer.

Version 1.0
-----------
This app is an inital release that provides the basic building blocks to tie searches to the data
sources that they access so that we can start answering the above questions.

Components
----------

- SA-search_profiling: contains a couple of dashboards that answer customers most basic 
   questions about data usage. Requires Treemap Custom Vizualization for visualing data
   volumes and search loads: https://splunkbase.splunk.com/app/3118/
- TA-search_profiling: contains the summary searches, custom commands, and lookups required 
   to generate the data to drive the analytics. Needs to be installed on ALL active search
   heads for complete coverage.
- SP-IndexCreation: contains the search_profiling index definition for use in distributed 
   or clustered indexer environments.


Some caveats:

- So far the app only looks at indexes and sourcetypes as these are the metadata fields that
   customers typically use to track their data. A small number of users may search based on 
   source or host rather than sourcetype making it difficult to evaluate which sourcetypes 
   are being touched. This may be a solveable problem down the road, but initially we're 
   making some assumptions and focusing on sourcetypes for simplicity. We've gone to great
   lengths to get as accurate as possible, but 100% accuracy is likely unattainable without more 
   detailed instrumentation from the product. Keep in mind that there is a small fudge factor,
   but we have fields the data that help us track when we are right on and when we are making
   assumptions.

- The TA nees to be installed on each search head for complete coverage and accurate 
   analysis. Not ideal, but one of the challenges in analyzing raw search strings is dealing 
   with macros, which are leveraged fairly often, especially in Splunk premium applications. 
   In order to accurately parse macros, the summary searches need to be run on the search 
   head where the original search ran.

- The summary searches depend on a handful of lookup files which populate frequently, every five
   to ten minutes. You may get some errors if you try to run the summary searches right away,
   but if you let things sit for a few minutes, the summary index should start populating 
   correctly once the lookup generating searches have had a chance to run.

- There are a lot of questions that could potentially be answered with this data, but we're 
   starting off very simply. The initial content is light, feedback is welcome! Let us know
   what questions you and your customers have about how their data is being used. 