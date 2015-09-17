(ns jeeves.core
  (:require [reagent.core :as r]))

(enable-console-print!)


(defonce state (r/atom (sorted-map)))


;; The wall clock showing seconds since a constant point in time quite some time
;; ago, before I was born.

(defn ms->s [ms]
  (quot ms 1000))

(defn current-seconds []
  (ms->s (. js/Date (now))))

(defonce now-seconds (r/atom (current-seconds)))

(js/setInterval #(swap! now-seconds current-seconds) 1000)


;; accept and delete builds, adding a birth timestamp to the build when we receive it.

(defn build-add-birth [build]
  (let [birth (- @now-seconds (:age-in-seconds build))]
    (assoc build :birth birth)))

(defn accept-builds [builds:js]
  (let [builds (->> (js->clj builds:js :keywordize-keys true)
                    (map build-add-birth))]
    (swap! state assoc :builds (zipmap (map :build-id builds) builds))))

(defn accept-build [build:js]
  (let [raw-build (js->clj build:js :keywordize-keys true)
        build (build-add-birth raw-build)]
    (swap! state assoc-in [:builds (:build-id build)] build)))

(defn delete-build [build-id:js]
  (let [build-id (js->clj build-id:js)]
    (swap! state update-in [:builds] dissoc build-id)))


;; A component displaying a rough age

(defn age->str-and-info [seconds]
  (js->clj (js/get-rough-time-difference-string seconds) :keywordize-keys true))

(defn age:c [birth]
  (let [now (r/atom (current-seconds))]
    (fn []
      (let [rough-age (age->str-and-info (- @now birth))]
        (js/setTimeout #(swap! now current-seconds) (* 1000 (:time_til_change rough-age)))
        [:span.age-display (str (:value rough-age) " ago")]))))


;; A component for displaying a duration exact to the second

(defn duration->str [seconds]
  (js->clj (js/get-exact-time-difference-string seconds)))

(defn duration:c [birth]
  [:span (duration->str (- @now-seconds birth))])


;; A component displaying the progress of a process with an estimated duration

(defn ->% [current total]
  (float (* 100 (/ current total))))

(defn progress-expected:c [progress text running?]
  (let [base-attrs {:style {:width (str progress "%")}}
        final-attrs (if running?
                      (assoc base-attrs :class "progress-bar-striped")
                      base-attrs)]
    [:div.progress-bar.progress-bar-success final-attrs text]))

(defn progress-overtime:c [progress]
  [:div.progress-bar.progress-bar-warning.progress-bar-striped {:style {:width (str progress "%")}}])

(defn progress:c [start maybe-initially-expected-duration]
  (let [initially-expected-duration (if-not maybe-initially-expected-duration
                                      300
                                      maybe-initially-expected-duration)
        duration-so-far (- @now-seconds start)]
    (if (<= duration-so-far initially-expected-duration)
      [:div.progress
       [progress-expected:c (->% duration-so-far initially-expected-duration) [duration:c start]]]
      (let [new-expected-duration (+ duration-so-far (- 60 (rem duration-so-far 60)))
            overtime (- duration-so-far initially-expected-duration)]
        [:div.progress
         [progress-expected:c (->% initially-expected-duration new-expected-duration) [duration:c start]]
         [progress-overtime:c (->% overtime new-expected-duration)]]))))


;; A component displaying a build as a table row

(defn build:c [build]
  [:tr.build-row.h4 {:id (:build-id build)}
   [:td.text-center {:style {:width "5%"}}
    [:a {:href (:view-url build)} \# (:build-id build)]]
   [:td.text-center {:style {:width "10%"}}
    (case (:status build)
      "scheduled" [:span.label.label-default.full-width "scheduled"]
      "blocked" [:span.label.label-default.full-width "blocked"]
      "cancelled" [:span.label.label-default.full-width "danger"]
      "running" [:span.label.label-warning.full-width "running"]
      "finished" (case (:result build)
                   "success" [:span.label.label-success.full-width "success"]
                   "failure" [:span.label.label-danger.full-width "failure"]
                   (:result build))
      (:status build))]
   [:td {:style {:width "10%"}} [age:c (:birth build)]]
   [:td {:style {:width "15%"}}
    (case (:status build)
      "running" [progress:c (:birth build) (:estimated-duration build)]
      "blocked" "waiting for build TODO-link"
      "finished" (str "ran for " (:duration build))
      (:status build))]
   [:td {:style {:width "2em" :height "2em" :padding "0"}}
    (when (:sender-avatar-url build)
      [:a {:href (:sender-html-url build) :target "_blank"}
       [:img {:src (:sender-avatar-url build)
              :style {:width "2em" :height "2em"}
              :title (str "github/" (:sender-login build))}]])]
   [:td {:style {:width "35%"}} (when (:branch-url build)
                                  [:a {:href (:branch-url build) :target "_blank"}
                                   [:span.fa.fa-github {:style {:font-size "1.1em"}}]
                                   (str " " (:branch build))])]
   [:td (:reason build)]
   [:td {:style {:width "7%"}}
    [:a.pull-right.btn.btn-default {:on-click #(js/do-action (:schedule-copy-url build))
                                    :role "button"
                                    :data-toggle "tooltip"
                                    :title "Schedule a copy of this build"}
     [:span.glyphicon.glyphicon-retweet]]
    (when (:cancellable? build)
      [:a.pull-right.btn.btn-default {:on-click #(js/do-action (:cancel-url build))
                                      :role "button"
                                      :data-toggle "tooltip"
                                      :title "Cancel this build"
                                      :style {:margin-right "0.3em"}}
       [:i.glyphicon.glyphicon-remove {:style {:color "red"}}]])]
   ])


;; A component displaying a list of builds as a table

(defn builds:c []
  (let [num-running ((->> (:builds @state)
                          (map second)
                          (map :status)
                          frequencies) "running" 0)
        builds-in-order (reverse (sort-by first (:builds @state)))]
    [:div
     [:h3 (str "Builds (" num-running " running)")]
     [:div.table-responsive
      [:table.table.table-striped>tbody
       (for [[build-id build] builds-in-order]
         ^{:key build-id} [build:c build])]]]))


(defn mount-build-list [root]
  (r/render-component [builds:c] root))
