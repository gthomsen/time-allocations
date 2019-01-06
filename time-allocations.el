;; Major mode for a (mostly) free-form, text-based time allocations file format.
;; Each allocations file contains category/subcategory allocation lines
;; separated by date lines, with all other lines being ignored.
;;
;; This mode provides basic facilities for efficiently entering allocations,
;; including the following:
;;
;;   * Syntax highlighting to identify the structure within allocations.
;;
;;   * Redefines paragraphs as single days for easy navigation.
;;
;;   * Keybindings for inserting time markers and date lines, as well as
;;     updating timelines and summarizing a day's allocations.
;;
;; Possible improvements:
;;
;;   * Add an idle timer callback (using post-command-hook) that summarizes the
;;     day-at-point's allocations.  The summary would either remain in the
;;     status buffer or be added to the mode line.  Movement in the buffer would
;;     cancel the previous callback's timer or reset the delay.
;;
;;   * Update ta-font-lock-keywords so lines that are potential allocations, but
;;     don't match the form imposed by ta-allocations-regexp, are highlighted.
;;     This would indicate lines that will generate a warning when parsed by a
;;     more strict tool.
;;
;;   * Provide a facility for a custom, possibly external, allocation summary
;;     so that more detailed/careful analysis can be presented within Emacs.
;;

;; provide an escape hatch for those who want even more customization
;; opportunities.
(defvar ta-mode-hook nil)

;; match a date line of the form:
;;
;;    <weekday> <month>/<date>
;;
(defvar ta-date-regexp "\\(\\(Mon\\|\\Tues\\|Wednes\\|Thurs\\|Fri\\|Satur\\|Sun\\)day[[:space:]]+[[:digit:]]+/[[:digit:]]+\\)")

;; match an allocation of the form:
;;
;;    <category>[ (<subcategory>[ (...)])]: X.Y hours
;;
;; NOTE: this regular expression does not validate the allocation makes sense
;;       (e.g. positive durations or properly formatted <category>/<subcategory>
;;       structures), only identifies lines that would be considered allocations
;;       for the sake of validation and parsing.
;;
(defvar ta-allocation-regexp ".+:[[:space:]]*\\([[:digit:]]+\\.[[:digit:]]*\\|\\(0?\\.0*\\)?[[:digit:]]+\\)[[:space:]]+hours?")

;; matches a timeline that is comprised of:
;;
;;   one or both of:
;;
;;     HH:MM-HH:MM    zero or more
;;     HH:MM-
;;
;;   optionally followed by:
;;
;;     (.*hour) or (.*hours)
;;
(defvar ta-timeline-regexp "\\(\\([[:space:]]*[[:digit:]]\\{2\\}:[[:digit:]]\\{2\\}-\\([[:digit:]]\\{2\\}:[[:digit:]]\\{2\\}\\)?\\)+\\([[:space:]]+(.*hours?)\\)?\\)")

;; number of minutes to round timeline times to.
(defvar ta-mode-time-granularity 15)

;; start a new day's allocations by inserting "<weekday> <month>/<date>" at the
;; point and adding an empty line.  note that zero padding is suppressed via the
;; "-" modifier in the time format string.
(defun ta-insert-current-date ()
  "Inserts the current date at the point."
  (interactive)
  (insert (format-time-string "%A %-m/%-d\n\n"))
)

;; insert the current time rounded to the nearest N-minutes.
(defun ta-insert-current-time ()
  "Inserts the current time, rounded to the nearest N minutes, at the point."
  (interactive)
  (let ((round-to-seconds (* 60 ta-mode-time-granularity)))
    (insert (format-time-string "%H:%M" (seconds-to-time
                                         (*
                                          (fround (/ (float-time) round-to-seconds))
                                          round-to-seconds)))))
)

;; convert a HH:MM string into the equivalent fractional hours value.
(defun ta-time-to-fractional-hours (time-string)
  "Converts a time string (of the form \"HH:MM\") to its duration in fractional hours."
  (interactive)
  ;; split at the colon and convert the hours and minutes into numeric values.
  (let* ((time-list (mapcar 'string-to-number (split-string time-string ":")))
         (hours   (car time-list))
         (minutes (car (cdr time-list))))
    (+ hours
       (/ minutes 60.0)))
)

;; update a timeline to include the correct duration.  adds a duration if it did
;; not include one, otherwise it updates the existing duration.
(defun ta-update-timeline (&optional quiet_flag)
  "Updates the current line's timeline and returns the total duration.  Optionally prints the timeline."
  (interactive)

  ;; don't bother summarizing if we're not on a timeline.
  (unless (string-match ta-timeline-regexp (thing-at-point 'line t))
    (error "Not on a timeline."))

  (let*
       ;; get the timeline into a string.
      ((timeline-text (thing-at-point 'line t))

       ;; build a list of range strings by 1) removing any trailing duration
       ;; note and 2) removing a trailing open duration.
       (duration-ranges (split-string (car (split-string timeline-text
                                                           "(.*hours?)" t "[[:space:]]"))
                                        "[[:digit:]]+:[[:digit:]]+-$" t "[[:space:]]"))

       ;; compute the duration of each range string and sum them.  take care to
       ;; handle timelines that consist only of a start time, or is an invalid
       ;; timeline line.
       (duration (if duration-ranges
                     (apply '+
                            ;; convert each range string into its duration.
                            (mapcar
                             (lambda (time-range)
                               (let* ((times-list (split-string time-range "-"))
                                      (start-time (ta-time-to-fractional-hours (car times-list)))
                                      (stop-time  (ta-time-to-fractional-hours (car (cdr times-list)))))
                                 (- stop-time start-time)))
                             (split-string (car duration-ranges))))
                   0))
       (duration-string (format "(%.2f hour%s)"
                                duration
                                (if (= duration 1)
                                    ""
                                  "s")))
       )

    (save-excursion
      (save-restriction
        ;; find the duration note at the end of the line and replace it.  or
        ;; simply insert it at the end of the line if it doesn't exist.
        (goto-char (point-at-bol))
        (narrow-to-region (point) (point-at-eol))
        (if (re-search-forward "(.*hours?)[[:space:]]*"
                               nil
                               t)
            (replace-match duration-string)
          (progn (goto-char (point-at-eol))
                 (insert " ")
                 (insert duration-string)))))

    ;; let the caller know the timeline summary.
    (unless quiet_flag
      (message "Time spent: %.2f hours" duration))

    duration
    )
)

(defun ta-summarize-current-allocations (&optional quiet_flag)
  "Summarizes the allocations for the day containing the point."
  (interactive)

  (save-excursion
    (save-restriction
      (let* ((allocation-bounds (bounds-of-thing-at-point 'paragraph))
             (duration 0))

        ;; restrict ourselves to today's allocations and position the point
        ;; at the beginning.
        (narrow-to-region (car allocation-bounds) (cdr allocation-bounds))
        (goto-char (point-min))

        ;; iterate through each line and sum the durations found in
        ;; allocation-like lines.
        ;;
        ;; NOTE: we don't do any serious validation of each line (e.g. ensure
        ;;       category/sub-categories are properly formed, or if the duration
        ;;       makes sense) since this is simply a tool to make allocation
        ;;       entry more efficient.
        ;;
        (while (< (point) (point-max))
          (let* ((current-line (thing-at-point 'line t)))
            (progn
              (if (string-match ta-allocation-regexp current-line)
                  (setq duration (+ duration
                                    (string-to-number (match-string-no-properties
                                                       1
                                                       current-line)))))

              (forward-line 1)
              )
            )
          )
        ;; let the caller know the allocation summary.
        (unless quiet_flag
          (message "Today a total of %.2f hours." duration))

        duration)
      )
    )
)

;; setup our keybindings to efficiently interact with allocations.
(defvar ta-mode-map
  (let ((map (make-sparse-keymap)))
    (define-key map (kbd "C-c d") 'ta-insert-current-date)
    (define-key map (kbd "C-c s") 'ta-summarize-current-allocations)
    (define-key map (kbd "C-c t") 'ta-insert-current-time)
    (define-key map (kbd "C-c u") 'ta-update-timeline)
    map)
  "Keymap for `time-allocation-mode'.")

;; update the syntax table so that "#" specifies a comment until the end of each
;; line they're found on.
(defvar ta-mode-syntax-table
  (let ((st (make-syntax-table)))
    (modify-syntax-entry ?# "<" st)
    (modify-syntax-entry ?\n ">" st)
    st)
  "Syntax table for `time-allocation-mode'.")

(defvar ta-font-lock-keywords
  ;; highlight "<weekday> <month>/<date>" so individual days are very clearly
  ;; identified.
  ;;
  ;; NOTE: we use a backtick (`) to expand the regular expression variables to
  ;;       strings, while everything else, remains as is.  specifying a variable
  ;;       here does not work and my Lisp is too limited to identify the proper
  ;;       approach.
  ;;
   `((,ta-date-regexp     . (1 font-lock-keyword-face))
     (,ta-timeline-regexp . (1 font-lock-function-name-face)))
  "Keyword highlighting specification for `time-allocation-mode'.")

(defun time-allocation-mode ()
  "A major mode for editing time allocation files."
  (interactive)
  (kill-all-local-variables)

  ;; define sentences/paragraphs/pages/etc so global keybindings behave as we
  ;; want.
  (set-syntax-table ta-mode-syntax-table)

  ;; add our keybindings.
  (use-local-map ta-mode-map)

  ;; redefine paragraphs to date lines for easy navigation.
  (setq-local paragraph-start    ta-date-regexp)
  (setq-local paragraph-separate ta-date-regexp)

  ;; turn on syntax highlighting.
  (setq-local font-lock-defaults '(ta-font-lock-keywords))
  (setq-local comment-start "#")
  (setq-local comment-start-skip "#+\\s-*")

  ;; set the mode's metadata.
  (setq mode-name "Time Allocations")
  (setq major-mode 'time-allocation-mode)

  ;; run any user-defined code.
  (run-hooks 'ta-mode-hook)
)

(provide 'time-allocation)
