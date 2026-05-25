(() => {
    const menuButton = document.querySelector("[data-menu-toggle]");
    const navMenu = document.querySelector("[data-nav-menu]");

    if (menuButton && navMenu) {
        menuButton.addEventListener("click", () => {
            navMenu.classList.toggle("show");
        });

        navMenu.querySelectorAll("a").forEach((link) => {
            link.addEventListener("click", () => {
                navMenu.classList.remove("show");
            });
        });

        document.addEventListener("click", (event) => {
            if (!navMenu.contains(event.target) && !menuButton.contains(event.target)) {
                navMenu.classList.remove("show");
            }
        });
    }

    const fileInput = document.getElementById("file-input");
    const dropZone = document.getElementById("drop-zone");
    const previewWrap = document.getElementById("preview-wrap");
    const previewImg = document.getElementById("preview-img");
    const previewName = document.getElementById("preview-name");
    const uploadForm = document.getElementById("upload-form");
    const loadingOverlay = document.getElementById("loading");

    if (fileInput && previewWrap && previewImg && previewName) {
        fileInput.addEventListener("change", () => {
            const file = fileInput.files && fileInput.files[0];
            if (!file) {
                return;
            }
            previewImg.src = URL.createObjectURL(file);
            previewName.textContent = `${file.name} (${(file.size / 1024).toFixed(1)} KB)`;
            previewWrap.style.display = "block";
        });
    }

    if (dropZone && fileInput) {
        ["dragenter", "dragover"].forEach((eventName) => {
            dropZone.addEventListener(eventName, (event) => {
                event.preventDefault();
                dropZone.classList.add("drag-over");
            });
        });

        ["dragleave", "drop"].forEach((eventName) => {
            dropZone.addEventListener(eventName, (event) => {
                event.preventDefault();
                dropZone.classList.remove("drag-over");
            });
        });

        dropZone.addEventListener("drop", (event) => {
            const file = event.dataTransfer && event.dataTransfer.files[0];
            if (!file) {
                return;
            }

            if (typeof DataTransfer !== "undefined") {
                const transfer = new DataTransfer();
                transfer.items.add(file);
                fileInput.files = transfer.files;
                fileInput.dispatchEvent(new Event("change"));
            }
        });
    }

    if (uploadForm && loadingOverlay) {
        uploadForm.addEventListener("submit", () => {
            loadingOverlay.classList.add("show");
        });
    }

    const patientUploadForm = document.querySelector("[data-patient-upload-form]");
    const patientUploadInput = document.querySelector("[data-patient-upload-input]");
    const patientUploadSubmit = document.querySelector("[data-patient-upload-submit]");
    const patientUploadDropzone = document.querySelector("[data-patient-upload-dropzone]");
    const patientUploadPreview = document.querySelector("[data-patient-upload-preview]");
    const patientUploadPreviewImage = document.querySelector("[data-patient-upload-preview-image]");
    const patientUploadPreviewName = document.querySelector("[data-patient-upload-preview-name]");
    const patientUploadProgress = document.querySelector("[data-patient-upload-progress]");
    const patientUploadFeedback = document.querySelector("[data-patient-upload-feedback]");

    if (
        patientUploadForm &&
        patientUploadInput &&
        patientUploadSubmit &&
        patientUploadDropzone &&
        patientUploadPreview &&
        patientUploadPreviewImage &&
        patientUploadPreviewName &&
        patientUploadProgress &&
        patientUploadFeedback
    ) {
        let previewObjectUrl = "";
        const allowedExt = new Set(["jpg", "jpeg", "png", "bmp", "webp"]);

        // i18n-aware messages. Read translated strings from the form's
        // data-msg-* attributes when present (set by the server via
        // {{ t(...) }}); fall back to the original English defaults when
        // missing so behavior is byte-identical on untranslated pages.
        // This change is text-only — upload/validation/submit logic is
        // untouched.
        const messages = {
            unsupported: patientUploadForm.dataset.msgUnsupported ||
                "Unsupported file type. Please select JPG, PNG, BMP, or WEBP.",
            selected: patientUploadForm.dataset.msgSelected ||
                "Image selected. Ready for AI analysis.",
            chooseFirst: patientUploadForm.dataset.msgChooseFirst ||
                "Please choose an image before starting analysis.",
            analyzing: patientUploadForm.dataset.msgAnalyzing ||
                "AI analysis is in progress. Please wait.",
            btnAnalyzing: patientUploadForm.dataset.msgBtnAnalyzing ||
                "Analyzing image...",
        };

        const setFeedback = (text, type = "") => {
            patientUploadFeedback.textContent = text || "";
            patientUploadFeedback.dataset.state = type;
        };

        const clearPreviewObjectUrl = () => {
            if (previewObjectUrl) {
                URL.revokeObjectURL(previewObjectUrl);
                previewObjectUrl = "";
            }
        };

        const setInputFile = (file) => {
            if (!file || typeof DataTransfer === "undefined") {
                return;
            }
            const transfer = new DataTransfer();
            transfer.items.add(file);
            patientUploadInput.files = transfer.files;
            patientUploadInput.dispatchEvent(new Event("change"));
        };

        patientUploadInput.addEventListener("change", () => {
            const file = patientUploadInput.files && patientUploadInput.files[0];
            clearPreviewObjectUrl();
            patientUploadPreview.hidden = true;
            setFeedback("", "");
            if (!file) {
                return;
            }

            const ext = (file.name.split(".").pop() || "").toLowerCase();
            if (!allowedExt.has(ext)) {
                patientUploadInput.value = "";
                setFeedback(messages.unsupported, "error");
                return;
            }

            previewObjectUrl = URL.createObjectURL(file);
            patientUploadPreviewImage.src = previewObjectUrl;
            patientUploadPreviewName.textContent = `${file.name} (${(file.size / 1024).toFixed(1)} KB)`;
            patientUploadPreview.hidden = false;
            setFeedback(messages.selected, "success");
        });

        ["dragenter", "dragover"].forEach((eventName) => {
            patientUploadDropzone.addEventListener(eventName, (event) => {
                event.preventDefault();
                patientUploadDropzone.classList.add("is-drag-over");
            });
        });

        ["dragleave", "drop"].forEach((eventName) => {
            patientUploadDropzone.addEventListener(eventName, (event) => {
                event.preventDefault();
                patientUploadDropzone.classList.remove("is-drag-over");
            });
        });

        patientUploadDropzone.addEventListener("drop", (event) => {
            const file = event.dataTransfer && event.dataTransfer.files && event.dataTransfer.files[0];
            if (!file) {
                return;
            }
            setInputFile(file);
        });

        patientUploadForm.addEventListener("submit", (event) => {
            const file = patientUploadInput.files && patientUploadInput.files[0];
            if (!file) {
                event.preventDefault();
                setFeedback(messages.chooseFirst, "error");
                return;
            }

            patientUploadSubmit.disabled = true;
            patientUploadSubmit.textContent = messages.btnAnalyzing;
            patientUploadForm.classList.add("is-analyzing");
            patientUploadProgress.hidden = false;
            setFeedback(messages.analyzing, "info");
        });
    }
})();

/* ============================================================
   SPLASH ANIMATION LOGIC  (REMOVABLE SECTION)
   ------------------------------------------------------------
   Self-contained handler for the opening logo animation.
   Independent IIFE: it does not touch auth, ML, /predict,
   patient isolation, or any other feature.

   To remove the animation completely:
     1. Delete this entire JS block (down to the matching
        END SPLASH ANIMATION LOGIC marker).
     2. Delete the splash HTML block in templates/index.html.
     3. Delete the "splash animation" CSS section in style.css.
   ============================================================ */
(function () {
    var splash = document.getElementById("ws-splash");
    if (!splash) {
        return;
    }

    var SESSION_KEY = "wsSplashShown";
    var docEl = document.documentElement;

    // Skip the animation if already shown earlier in this session.
    try {
        if (window.sessionStorage && sessionStorage.getItem(SESSION_KEY) === "1") {
            if (splash.parentNode) {
                splash.parentNode.removeChild(splash);
            }
            return;
        }
    } catch (e) {
        // sessionStorage may be unavailable (private mode, etc.) — fall through.
    }

    // Respect users who prefer reduced motion.
    var prefersReduced = window.matchMedia &&
        window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    // Total visible time, then fade out, then DOM cleanup.
    // Tuned for ~2.7s total premium feel (entrance + hold + fade).
    var visibleMs = prefersReduced ? 900 : 2200;   // logo on screen
    var fadeMs    = prefersReduced ? 250 : 500;    // fade-out duration

    // Lock page scroll while splash is on screen.
    docEl.classList.add("ws-splash-lock");

    // Mark as shown for this session immediately so refresh during
    // animation does not double-show it.
    try {
        if (window.sessionStorage) {
            sessionStorage.setItem(SESSION_KEY, "1");
        }
    } catch (e) {
        // ignore
    }

    // Trigger fade-out.
    var fadeTimer = window.setTimeout(function () {
        splash.classList.add("ws-splash--exit");
    }, visibleMs);

    // Cleanup: remove splash from DOM and unlock scroll.
    var cleanupTimer = window.setTimeout(function () {
        docEl.classList.remove("ws-splash-lock");
        if (splash.parentNode) {
            splash.parentNode.removeChild(splash);
        }
    }, visibleMs + fadeMs + 50);

    // Safety net: if the user clicks/taps anywhere, dismiss early.
    splash.addEventListener("click", function () {
        window.clearTimeout(fadeTimer);
        window.clearTimeout(cleanupTimer);
        splash.classList.add("ws-splash--exit");
        window.setTimeout(function () {
            docEl.classList.remove("ws-splash-lock");
            if (splash.parentNode) {
                splash.parentNode.removeChild(splash);
            }
        }, fadeMs + 20);
    }, { once: true });
})();
/* ============================================================
   END SPLASH ANIMATION LOGIC
   ============================================================ */
