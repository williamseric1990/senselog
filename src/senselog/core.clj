(ns senselog.core
  (:require [aleph.udp :as udp]
            [manifold.stream :as s]
            [msgpack.core :as msgpack])
  (:gen-class))

(def DATA-ID    "\u0001\u0000")
(def DATA-REQ   "\u0001\u0001")
(def DATA-ERROR "\u0001\u0002")

(def client-socket @(udp/socket {}))

(def address {:host "localhost"
              :port 3000})

(defn log [tag message]
  (let [now (java.util.Date.)]
   (println (str "[" (.format (java.text.SimpleDateFormat. "yyyy-MM-dd'T'HH:mm:ssZ") now) "] [" tag "] " message))))

(defn pack-sensed-packet [header data]
  (str header (String. (msgpack/pack data))))

(defn unpack-sensed-packet [packet]
  (msgpack/unpack (drop 2 packet)))

(defn get-meta []
 (s/put! client-socket (assoc address :message (String. DATA-ID)))
 @(s/take! client-socket))

(defn get-sensors []
  (s/put! client-socket (assoc address :message (pack-sensed-packet DATA-REQ "")))
  @(s/take! client-socket))

(defn -main
  "I don't do a whole lot ... yet."
  [& args]
  (let [meta-data (unpack-sensed-packet (:message (get-meta)))]
    (log "INFO" "Node Metadata")
    (log "\\\\\\/" "=============")
    (log "INFO" (str "Name: " (get meta-data "name")))
    (log "INFO" (str "Sensors: " (clojure.string/join ", " (get meta-data "sensors")))))
  (log "\\\\\\/" "")
  (get-sensors) ; without this line, no data is recieved (???)
  (let [sensor-data (unpack-sensed-packet (:message (get-sensors)))]
    (log "INFO" "Node Sensor Data")
    (log "\\\\\\/" "================")
    (doseq [keyval (get sensor-data "sensors")]
      (log "INFO" keyval))))

