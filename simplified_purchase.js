
// ============================================================================
// SIMPLIFIED PURCHASE REPORT - Clean Working Implementation (OVERRIDES BROKEN VERSION)
// ============================================================================
window.purchaseReport = async function purchaseReport() {
    console.log("✅ purchaseReport called (simplified version)");
    
    // Prevent multiple calls
    if (window._purchaseInProgress) {
        console.log("⏳ Purchase already in progress");
        return;
    }
    window._purchaseInProgress = true;
    
    try {
        // 1. Check report type
        if (!window.selectedReportType) {
            const selectedCard = document.querySelector(".report-type-card.selected");
            if (selectedCard) {
                window.selectedReportType = selectedCard.dataset.type || "";
                window.selectedReportPrice = selectedCard.dataset.price || "0";
            }
        }
        
        if (!window.selectedReportType) {
            if (window.notificationSystem) {
                window.notificationSystem.showError("Error", "Please select a report type first.");
            } else {
                alert("Please select a report type first.");
            }
            window._purchaseInProgress = false;
            return;
        }
        
        // 2. Get form data
        const safeStorage = window.safeStorage || { getItem: () => null, setItem: () => {}, removeItem: () => {} };
        const token = safeStorage.getItem("auth_token") || safeStorage.getItem("crane_auth_token");
        
        const formData = {
            manufacturer: document.getElementById("manufacturer")?.value || "",
            model: document.getElementById("model")?.value || "",
            year: document.getElementById("year")?.value || "",
            capacity: document.getElementById("capacity")?.value || "",
            operatingHours: document.getElementById("operatingHours")?.value || "",
            region: document.getElementById("region")?.value || "North America",
            craneType: document.getElementById("craneType")?.value || "",
            boomLength: document.getElementById("boomLength")?.value || "",
            mileage: document.getElementById("mileage")?.value || "",
            reportType: window.selectedReportType,
            price: window.selectedReportPrice
        };
        
        // 3. Validate required fields
        if (!formData.manufacturer || !formData.model || !formData.year || !formData.capacity) {
            if (window.notificationSystem) {
                window.notificationSystem.showError("Validation Error", "Please fill in all required fields (Manufacturer, Model, Year, Capacity).");
            } else {
                alert("Please fill in all required fields.");
            }
            window._purchaseInProgress = false;
            return;
        }
        
        // 4. Create draft report
        let draftReportId = null;
        if (token) {
            try {
                const draftResponse = await fetch("/api/v1/fmv-reports/draft", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "Authorization": `Bearer ${token}`
                    },
                    body: JSON.stringify(formData)
                });
                
                if (draftResponse.ok) {
                    const draftData = await draftResponse.json();
                    draftReportId = draftData.id || draftData.report_id;
                    window.currentDraftReportId = draftReportId;
                    console.log("✅ Draft report created:", draftReportId);
                } else {
                    console.warn("⚠️ Draft creation failed, continuing anyway");
                }
            } catch (e) {
                console.error("Error creating draft:", e);
                // Continue anyway
            }
        }
        
        // 5. Open payment modal
        const paymentModal = document.getElementById("paymentModal");
        if (paymentModal) {
            paymentModal.style.display = "flex";
            paymentModal.style.visibility = "visible";
            paymentModal.removeAttribute("data-force-hidden");
            
            // Initialize Stripe if available
            if (typeof window.initializeStripe === "function") {
                try {
                    await window.initializeStripe();
                } catch (e) {
                    console.error("Error initializing Stripe:", e);
                }
            }
            
            // Store data for after payment
            window.lastPaymentData = {
                draftReportId: draftReportId,
                formData: formData,
                reportType: window.selectedReportType,
                price: window.selectedReportPrice
            };
            
            console.log("✅ Payment modal opened");
        } else {
            console.error("❌ Payment modal not found");
            if (window.notificationSystem) {
                window.notificationSystem.showError("Error", "Payment modal not found. Please refresh the page.");
            } else {
                alert("Payment modal not found. Please refresh the page.");
            }
        }
        
    } catch (e) {
        console.error("Error in purchaseReport:", e);
        if (window.notificationSystem) {
            window.notificationSystem.showError("Error", "Failed to initiate purchase: " + e.message);
        } else {
            alert("Failed to initiate purchase: " + e.message);
        }
    } finally {
        window._purchaseInProgress = false;
    }
};
console.log("✅ Simplified purchaseReport function ready");
