// Enhanced Crane Valuation System - Based on Professional Terminal Analysis
// Implements comprehensive scoring, deal analysis, and financial breakdown

class EnhancedCraneValuation {
    constructor() {
        this.marketData = this.initializeMarketData();
        this.manufacturerProfiles = this.initializeManufacturerProfiles();
        this.regionalFactors = this.initializeRegionalFactors();
    }

    // Initialize comprehensive market data
    initializeMarketData() {
        return {
            baseRates: {
                'Crawler Crane': 5000,
                'All-Terrain Crane': 4500,
                'Rough Terrain Crane': 4000,
                'Truck-Mounted Crane': 3500,
                'Telescopic Crawler Crane': 4800
            },
            marketTrends: {
                'North America': { demand: 1.04, supply: 0.96, volatility: 0.12 },
                'Europe': { demand: 1.02, supply: 0.98, volatility: 0.08 },
                'Asia Pacific': { demand: 1.01, supply: 0.99, volatility: 0.15 },
                'Middle East': { demand: 1.03, supply: 0.97, volatility: 0.18 },
                'Africa': { demand: 0.98, supply: 1.02, volatility: 0.25 },
                'South America': { demand: 0.99, supply: 1.01, volatility: 0.20 }
            },
            utilizationRates: {
                'North America': 0.71,
                'Europe': 0.68,
                'Asia Pacific': 0.65,
                'Middle East': 0.73,
                'Africa': 0.58,
                'South America': 0.62
            }
        };
    }

    // Initialize manufacturer profiles with comprehensive scoring
    initializeManufacturerProfiles() {
        return {
            'Liebherr': {
                premium: 0.15,
                reliability: 0.95,
                resaleValue: 0.90,
                marketShare: 0.25,
                reputation: 'Premium',
                dealScore: 0.85
            },
            'Grove': {
                premium: 0.10,
                reliability: 0.88,
                resaleValue: 0.85,
                marketShare: 0.20,
                reputation: 'High',
                dealScore: 0.80
            },
            'Tadano': {
                premium: 0.12,
                reliability: 0.92,
                resaleValue: 0.88,
                marketShare: 0.18,
                reputation: 'Premium',
                dealScore: 0.82
            },
            'Manitowoc': {
                premium: 0.08,
                reliability: 0.85,
                resaleValue: 0.82,
                marketShare: 0.15,
                reputation: 'Good',
                dealScore: 0.75
            },
            'Terex': {
                premium: 0.05,
                reliability: 0.80,
                resaleValue: 0.78,
                marketShare: 0.12,
                reputation: 'Good',
                dealScore: 0.70
            },
            'Link-Belt': {
                premium: 0.03,
                reliability: 0.82,
                resaleValue: 0.80,
                marketShare: 0.08,
                reputation: 'Good',
                dealScore: 0.72
            },
            'Kobelco': {
                premium: 0.10,
                reliability: 0.87,
                resaleValue: 0.84,
                marketShare: 0.10,
                reputation: 'High',
                dealScore: 0.78
            },
            'Sany': {
                premium: 0.02,
                reliability: 0.75,
                resaleValue: 0.70,
                marketShare: 0.15,
                reputation: 'Value',
                dealScore: 0.65
            }
        };
    }

    // Initialize regional factors
    initializeRegionalFactors() {
        return {
            'North America': { factor: 0.04, liquidity: 0.90, risk: 0.15 },
            'Europe': { factor: 0.02, liquidity: 0.85, risk: 0.12 },
            'Asia Pacific': { factor: 0.01, liquidity: 0.80, risk: 0.18 },
            'Middle East': { factor: 0.03, liquidity: 0.75, risk: 0.25 },
            'Africa': { factor: -0.02, liquidity: 0.60, risk: 0.35 },
            'South America': { factor: -0.01, liquidity: 0.65, risk: 0.30 }
        };
    }

    // Main comprehensive valuation function
    calculateComprehensiveValuation(formData) {
        console.log('🧮 Starting Enhanced Comprehensive Valuation...');
        
        try {
            // Step 1: Base Value Calculation
            const baseAnalysis = this.calculateBaseValue(formData);
            
            // Step 2: Deal & Wear Score Analysis
            const dealWearAnalysis = this.calculateDealWearScores(formData, baseAnalysis);
            
            // Step 3: Market Intelligence Analysis
            const marketAnalysis = this.calculateMarketIntelligence(formData);
            
            // Step 4: Financial Analysis
            const financialAnalysis = this.calculateFinancialAnalysis(baseAnalysis, dealWearAnalysis);
            
            // Step 5: Risk Assessment
            const riskAnalysis = this.calculateRiskAssessment(formData, dealWearAnalysis);
            
            // Step 6: ROI & Financing Analysis
            const roiAnalysis = this.calculateROIAnalysis(financialAnalysis, formData);
            
            // Step 7: Rent vs Buy Analysis
            const rentBuyAnalysis = this.calculateRentBuyAnalysis(financialAnalysis, formData);
            
            // Compile comprehensive result
            const comprehensiveResult = {
                // Core Valuation
                fairMarketValue: financialAnalysis.fairMarketValue,
                valuationRange: financialAnalysis.valuationRange,
                confidenceLevel: financialAnalysis.confidenceLevel,
                
                // Deal Analysis
                dealScore: dealWearAnalysis.dealScore,
                wearScore: dealWearAnalysis.wearScore,
                overallRecommendation: dealWearAnalysis.overallRecommendation,
                
                // Market Intelligence
                marketClassification: marketAnalysis.classification,
                marketTrend: marketAnalysis.trend,
                liquidityOutlook: marketAnalysis.liquidityOutlook,
                
                // Financial Analysis
                baseValue: baseAnalysis.baseValue,
                adjustments: baseAnalysis.adjustments,
                residualValue: financialAnalysis.residualValue,
                
                // Risk Analysis
                riskFactors: riskAnalysis.riskFactors,
                overallRiskScore: riskAnalysis.overallRiskScore,
                
                // ROI Analysis
                financingOptions: roiAnalysis.financingOptions,
                recommendedFinancing: roiAnalysis.recommendedFinancing,
                expectedROI: roiAnalysis.expectedROI,
                
                // Rent vs Buy
                rentBuyAnalysis: rentBuyAnalysis,
                
                // Detailed Breakdown
                detailedBreakdown: {
                    baseValueCalculation: baseAnalysis.detailedBreakdown,
                    dealWearBreakdown: dealWearAnalysis.breakdown,
                    marketIntelligence: marketAnalysis.detailedBreakdown,
                    riskBreakdown: riskAnalysis.detailedBreakdown
                }
            };
            
            console.log('✅ Enhanced Comprehensive Valuation Completed');
            return comprehensiveResult;
            
        } catch (error) {
            console.error('❌ Enhanced Valuation Error:', error);
            throw error;
        }
    }

    // Calculate base value with detailed breakdown
    calculateBaseValue(formData) {
        const craneType = formData.craneType || 'Crawler Crane';
        const baseRate = this.marketData.baseRates[craneType] || 5000;
        const capacityBasePrice = formData.capacity * baseRate;
        
        const manufacturerProfile = this.manufacturerProfiles[formData.manufacturer] || this.manufacturerProfiles['Terex'];
        const manufacturerPremium = capacityBasePrice * manufacturerProfile.premium;
        
        const modelPremium = this.calculateModelPremium(formData.model, capacityBasePrice);
        const baseValue = capacityBasePrice + manufacturerPremium + modelPremium;
        
        // Calculate adjustments
        const currentYear = new Date().getFullYear();
        const age = currentYear - formData.year;
        const ageDepreciation = this.calculateAgeDepreciation(baseValue, age);
        const hoursAdjustment = this.calculateHoursAdjustment(baseValue, formData.hours, age);
        const regionalFactor = this.calculateRegionalFactor(baseValue, formData.region);
        const marketConditions = this.calculateMarketConditions(baseValue, formData.region);
        const conditionAdjustment = this.calculateConditionAdjustment(baseValue, formData.condition);
        
        const totalAdjustments = ageDepreciation + hoursAdjustment + regionalFactor + marketConditions + conditionAdjustment;
        const finalValue = baseValue + totalAdjustments;
        
        return {
            baseValue: baseValue,
            adjustments: totalAdjustments,
            finalValue: finalValue,
            detailedBreakdown: {
                capacityBasePrice: capacityBasePrice,
                manufacturerPremium: manufacturerPremium,
                modelPremium: modelPremium,
                ageDepreciation: ageDepreciation,
                hoursAdjustment: hoursAdjustment,
                regionalFactor: regionalFactor,
                marketConditions: marketConditions,
                conditionAdjustment: conditionAdjustment
            }
        };
    }

    // Calculate Deal & Wear Scores
    calculateDealWearScores(formData, baseAnalysis) {
        const manufacturerProfile = this.manufacturerProfiles[formData.manufacturer] || this.manufacturerProfiles['Terex'];
        const currentYear = new Date().getFullYear();
        const age = currentYear - formData.year;
        
        // Deal Score Components
        const priceValue = this.calculatePriceValueScore(baseAnalysis.finalValue, formData);
        const marketTiming = this.calculateMarketTimingScore(formData);
        const condition = this.calculateConditionScore(formData.condition);
        const liquidity = this.calculateLiquidityScore(formData.manufacturer, formData.region);
        const risk = this.calculateRiskScore(formData, age);
        
        const dealScore = Math.round((priceValue + marketTiming + liquidity + risk) / 4);
        
        // Wear Score
        const wearScore = this.calculateWearScore(formData.hours, age, formData.condition);
        
        // Overall Recommendation
        const overallRecommendation = this.determineOverallRecommendation(dealScore, wearScore);
        
        return {
            dealScore: dealScore,
            wearScore: wearScore,
            overallRecommendation: overallRecommendation,
            breakdown: {
                priceValue: priceValue,
                marketTiming: marketTiming,
                condition: condition,
                liquidity: liquidity,
                risk: risk
            }
        };
    }

    // Calculate Market Intelligence
    calculateMarketIntelligence(formData) {
        const regionalData = this.marketData.marketTrends[formData.region];
        const utilizationRate = this.marketData.utilizationRates[formData.region];
        
        const classification = this.determineMarketClassification(formData);
        const trend = this.determineMarketTrend(regionalData);
        const liquidityOutlook = this.determineLiquidityOutlook(formData.manufacturer, formData.region);
        
        return {
            classification: classification,
            trend: trend,
            liquidityOutlook: liquidityOutlook,
            detailedBreakdown: {
                regionalData: regionalData,
                utilizationRate: utilizationRate,
                marketDemand: regionalData.demand,
                supplyLevel: regionalData.supply,
                volatility: regionalData.volatility
            }
        };
    }

    // Calculate Financial Analysis
    calculateFinancialAnalysis(baseAnalysis, dealWearAnalysis) {
        const fairMarketValue = baseAnalysis.finalValue;
        const confidenceLevel = this.calculateConfidenceLevel(dealWearAnalysis.dealScore);
        const valuationRange = this.calculateValuationRange(fairMarketValue, confidenceLevel);
        const residualValue = this.calculateResidualValue(fairMarketValue, dealWearAnalysis.wearScore);
        
        return {
            fairMarketValue: fairMarketValue,
            valuationRange: valuationRange,
            confidenceLevel: confidenceLevel,
            residualValue: residualValue
        };
    }

    // Calculate Risk Assessment
    calculateRiskAssessment(formData, dealWearAnalysis) {
        const marketRisk = this.calculateMarketRisk(formData.region);
        const conditionRisk = this.calculateConditionRisk(dealWearAnalysis.wearScore);
        const ageRisk = this.calculateAgeRisk(formData.year);
        const locationRisk = this.calculateLocationRisk(formData.region);
        
        const overallRiskScore = Math.round((marketRisk + conditionRisk + ageRisk + locationRisk) / 4);
        
        return {
            riskFactors: {
                marketRisk: marketRisk,
                conditionRisk: conditionRisk,
                ageRisk: ageRisk,
                locationRisk: locationRisk
            },
            overallRiskScore: overallRiskScore,
            detailedBreakdown: {
                marketRiskFactors: this.getMarketRiskFactors(formData.region),
                conditionRiskFactors: this.getConditionRiskFactors(dealWearAnalysis.wearScore),
                ageRiskFactors: this.getAgeRiskFactors(formData.year),
                locationRiskFactors: this.getLocationRiskFactors(formData.region)
            }
        };
    }

    // Calculate ROI Analysis
    calculateROIAnalysis(financialAnalysis, formData) {
        const fmv = financialAnalysis.fairMarketValue;
        const financingOptions = this.calculateFinancingOptions(fmv);
        const recommendedFinancing = this.determineRecommendedFinancing(financingOptions);
        const expectedROI = this.calculateExpectedROI(fmv, recommendedFinancing);
        
        return {
            financingOptions: financingOptions,
            recommendedFinancing: recommendedFinancing,
            expectedROI: expectedROI
        };
    }

    // Calculate Rent vs Buy Analysis
    calculateRentBuyAnalysis(financialAnalysis, formData) {
        const monthlyRental = this.calculateMonthlyRental(financialAnalysis.fairMarketValue, formData);
        const fiveYearRentalCost = monthlyRental * 60;
        const fiveYearOwnershipCost = this.calculateFiveYearOwnershipCost(financialAnalysis.fairMarketValue);
        const savingsByBuying = fiveYearRentalCost - fiveYearOwnershipCost;
        const breakEvenPeriod = this.calculateBreakEvenPeriod(monthlyRental, financialAnalysis.fairMarketValue);
        
        return {
            monthlyRental: monthlyRental,
            fiveYearRentalCost: fiveYearRentalCost,
            fiveYearOwnershipCost: fiveYearOwnershipCost,
            savingsByBuying: savingsByBuying,
            breakEvenPeriod: breakEvenPeriod,
            recommendation: savingsByBuying > 0 ? 'BUY' : 'RENT'
        };
    }

    // Helper calculation methods
    calculateModelPremium(model, basePrice) {
        if (model.includes('LR 1800') || model.includes('LTM 1500')) return basePrice * 0.08;
        if (model.includes('GMK') || model.includes('ATF')) return basePrice * 0.06;
        if (model.includes('CK') || model.includes('MLC')) return basePrice * 0.04;
        return basePrice * 0.05;
    }

    calculateAgeDepreciation(baseValue, age) {
        if (age <= 2) return 0;
        if (age <= 5) return -baseValue * 0.05 * age;
        if (age <= 10) return -baseValue * 0.08 * age;
        return -baseValue * 0.12 * age;
    }

    calculateHoursAdjustment(baseValue, hours, age) {
        const expectedHours = age * 800;
        if (hours === 0) return -baseValue * 0.10;
        if (hours < expectedHours * 0.7) return baseValue * 0.05;
        if (hours < expectedHours * 1.3) return 0;
        return -baseValue * 0.03;
    }

    calculateRegionalFactor(baseValue, region) {
        const regionalData = this.regionalFactors[region];
        return baseValue * (regionalData ? regionalData.factor : 0.02);
    }

    calculateMarketConditions(baseValue, region) {
        const regionalData = this.marketData.marketTrends[region];
        return baseValue * (regionalData ? regionalData.demand - 1 : 0.03);
    }

    calculateConditionAdjustment(baseValue, condition) {
        if (condition >= 0.9) return baseValue * 0.05;
        if (condition >= 0.8) return baseValue * 0.03;
        if (condition >= 0.7) return baseValue * 0.01;
        if (condition >= 0.6) return -baseValue * 0.02;
        return -baseValue * 0.05;
    }

    // Additional helper methods for comprehensive analysis
    calculatePriceValueScore(finalValue, formData) {
        // Compare against market benchmarks
        const marketBenchmark = formData.capacity * 4500; // Industry average
        const valueRatio = marketBenchmark / finalValue;
        return Math.min(100, Math.max(0, valueRatio * 100));
    }

    calculateMarketTimingScore(formData) {
        const regionalData = this.marketData.marketTrends[formData.region];
        const demandFactor = regionalData ? regionalData.demand : 1.0;
        return Math.min(100, Math.max(0, demandFactor * 90));
    }

    calculateConditionScore(condition) {
        return Math.round(condition * 100);
    }

    calculateLiquidityScore(manufacturer, region) {
        const manufacturerProfile = this.manufacturerProfiles[manufacturer];
        const regionalData = this.regionalFactors[region];
        const liquidityScore = (manufacturerProfile.resaleValue + regionalData.liquidity) / 2;
        return Math.round(liquidityScore * 100);
    }

    calculateRiskScore(formData, age) {
        const manufacturerProfile = this.manufacturerProfiles[formData.manufacturer];
        const regionalData = this.regionalFactors[formData.region];
        const riskScore = (manufacturerProfile.reliability + (1 - regionalData.risk)) / 2;
        return Math.round(riskScore * 100);
    }

    calculateWearScore(hours, age, condition) {
        const expectedHours = age * 800;
        const hoursRatio = hours / expectedHours;
        const conditionScore = condition * 100;
        const wearScore = Math.max(0, 100 - (hoursRatio * 30) - (100 - conditionScore) * 0.5);
        return Math.round(wearScore);
    }

    determineOverallRecommendation(dealScore, wearScore) {
        if (dealScore >= 90 && wearScore >= 70) return 'Strong Buy';
        if (dealScore >= 80 && wearScore >= 60) return 'Buy';
        if (dealScore >= 70 && wearScore >= 50) return 'Hold';
        if (dealScore >= 60 && wearScore >= 40) return 'Caution';
        return 'Avoid';
    }

    // Additional helper methods for market intelligence, risk assessment, etc.
    determineMarketClassification(formData) {
        if (formData.capacity >= 500) return 'Heavy Duty';
        if (formData.capacity >= 250) return 'Mid Range';
        if (formData.capacity >= 100) return 'Standard';
        return 'Light Duty';
    }

    determineMarketTrend(regionalData) {
        if (regionalData.demand > 1.05) return 'Strong Growth';
        if (regionalData.demand > 1.02) return 'Moderate Growth';
        if (regionalData.demand > 0.98) return 'Stable';
        return 'Declining';
    }

    determineLiquidityOutlook(manufacturer, region) {
        const manufacturerProfile = this.manufacturerProfiles[manufacturer];
        const regionalData = this.regionalFactors[region];
        const liquidityScore = (manufacturerProfile.resaleValue + regionalData.liquidity) / 2;
        
        if (liquidityScore >= 0.85) return 'Excellent';
        if (liquidityScore >= 0.75) return 'Good';
        if (liquidityScore >= 0.65) return 'Fair';
        return 'Poor';
    }

    calculateConfidenceLevel(dealScore) {
        if (dealScore >= 90) return 'HIGH';
        if (dealScore >= 80) return 'MEDIUM';
        return 'LOW';
    }

    calculateValuationRange(fmv, confidenceLevel) {
        const variance = confidenceLevel === 'HIGH' ? 0.10 : confidenceLevel === 'MEDIUM' ? 0.15 : 0.20;
        return {
            low: fmv * (1 - variance),
            high: fmv * (1 + variance)
        };
    }

    calculateResidualValue(fmv, wearScore) {
        const residualFactor = Math.max(0.5, wearScore / 100);
        return fmv * residualFactor;
    }

    // Risk calculation methods
    calculateMarketRisk(region) {
        const regionalData = this.marketData.marketTrends[region];
        return Math.round(regionalData.volatility * 100);
    }

    calculateConditionRisk(wearScore) {
        return Math.round(100 - wearScore);
    }

    calculateAgeRisk(year) {
        const age = new Date().getFullYear() - year;
        if (age <= 5) return 20;
        if (age <= 10) return 40;
        if (age <= 15) return 60;
        return 80;
    }

    calculateLocationRisk(region) {
        const regionalData = this.regionalFactors[region];
        return Math.round(regionalData.risk * 100);
    }

    // Financing and ROI methods
    calculateFinancingOptions(fmv) {
        return {
            cashPurchase: {
                downPayment: fmv,
                term: 0,
                rate: 0,
                monthly: 0,
                roi: 0.27
            },
            standardFinance: {
                downPayment: fmv * 0.20,
                term: 60,
                rate: 0.065,
                monthly: this.calculateMonthlyPayment(fmv * 0.80, 0.065, 60),
                roi: 0.18
            },
            lowDownFinance: {
                downPayment: fmv * 0.10,
                term: 72,
                rate: 0.075,
                monthly: this.calculateMonthlyPayment(fmv * 0.90, 0.075, 72),
                roi: 0.16
            },
            extendedTerm: {
                downPayment: fmv * 0.15,
                term: 84,
                rate: 0.085,
                monthly: this.calculateMonthlyPayment(fmv * 0.85, 0.085, 84),
                roi: 0.15
            }
        };
    }

    calculateMonthlyPayment(principal, rate, months) {
        const monthlyRate = rate / 12;
        return principal * (monthlyRate * Math.pow(1 + monthlyRate, months)) / (Math.pow(1 + monthlyRate, months) - 1);
    }

    determineRecommendedFinancing(financingOptions) {
        // Logic to determine best financing option based on ROI and terms
        return 'standardFinance';
    }

    calculateExpectedROI(fmv, recommendedFinancing) {
        const option = this.calculateFinancingOptions(fmv)[recommendedFinancing];
        return option.roi;
    }

    calculateMonthlyRental(fmv, formData) {
        const baseRentalRate = fmv * 0.015; // 1.5% of value per month
        const regionalMultiplier = this.regionalFactors[formData.region].factor + 1;
        return baseRentalRate * regionalMultiplier;
    }

    calculateFiveYearOwnershipCost(fmv) {
        const maintenance = fmv * 0.15; // 3% per year for 5 years
        const insurance = fmv * 0.075; // 1.5% per year for 5 years
        const storage = 12000 * 5; // $12K per year for 5 years
        const depreciation = fmv * 0.30; // 30% depreciation over 5 years
        return fmv + maintenance + insurance + storage - depreciation;
    }

    calculateBreakEvenPeriod(monthlyRental, fmv) {
        const annualRental = monthlyRental * 12;
        const annualOwnership = fmv * 0.20; // Simplified annual ownership cost
        const annualSavings = annualRental - annualOwnership;
        return Math.ceil(fmv / annualSavings);
    }

    // Risk factor details
    getMarketRiskFactors(region) {
        const regionalData = this.marketData.marketTrends[region];
        return {
            volatility: regionalData.volatility,
            demandTrend: regionalData.demand,
            supplyLevel: regionalData.supply
        };
    }

    getConditionRiskFactors(wearScore) {
        return {
            wearLevel: wearScore < 50 ? 'High' : wearScore < 70 ? 'Medium' : 'Low',
            maintenanceRequired: wearScore < 60 ? 'Extensive' : wearScore < 80 ? 'Moderate' : 'Minimal'
        };
    }

    getAgeRiskFactors(year) {
        const age = new Date().getFullYear() - year;
        return {
            ageCategory: age <= 5 ? 'New' : age <= 10 ? 'Mid-life' : age <= 15 ? 'Mature' : 'Vintage',
            technologyLevel: age <= 5 ? 'Current' : age <= 10 ? 'Recent' : age <= 15 ? 'Legacy' : 'Obsolete'
        };
    }

    getLocationRiskFactors(region) {
        const regionalData = this.regionalFactors[region];
        return {
            liquidityRisk: regionalData.liquidity < 0.7 ? 'High' : regionalData.liquidity < 0.8 ? 'Medium' : 'Low',
            politicalRisk: regionalData.risk > 0.25 ? 'High' : regionalData.risk > 0.15 ? 'Medium' : 'Low'
        };
    }
}

// Export for use in the main application
window.EnhancedCraneValuation = EnhancedCraneValuation;
