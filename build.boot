(set-env!
 :source-paths #{"src"}
 :dependencies '[[adzerk/boot-cljs "1.7.48-3" :scope "test"]
                 [org.clojure/clojure "1.7.0"]
                 [org.clojure/clojurescript "1.7.122"]
                 [reagent "0.5.1"]])

(require
 '[adzerk.boot-cljs :refer :all])

(deftask dev []
  (comp (watch)
        (speak)
        (cljs :source-map true :optimizations :none)))

(deftask build []
  (cljs :optimizations :advanced))
