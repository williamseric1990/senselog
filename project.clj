(defproject senselog "0.1.0-SNAPSHOT"
  :description "A reference server implementation for sensed clients."
  :url "http://github.com/sli/senselog/tree/clojure"
  :license {:name "MIT"
            :url "https://opensource.org/licenses/MIT"}
  :dependencies [[org.clojure/clojure "1.8.0"]
                 [aleph "0.4.1"]
                 [clojure-msgpack "1.2.0"]]
  :main ^:skip-aot senselog.core
  :target-path "target/%s"
  :profiles {:uberjar {:aot :all}})
