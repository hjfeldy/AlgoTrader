#include <iostream>
#include <vector>
#include <string>
#include <cmath>
#include <fstream>

#define RESET   "\033[0m"
#define RED     "\033[31m"
#define GREEN   "\033[32m"


std::vector<double> go(std::vector<double> prices, double window) {
    // Create instantaneous changes vector
    std::vector<double> changes = {0};
    for(int i = 1; i < prices.size(); i++) {
        double change = (prices[i] - prices[i - 1]) / prices[i - 1];
        change *= 100;
        changes.push_back(change);
    }
    // Create rolling avg vector
    std::vector<double> smooth;
    double total = 0;
    
    for(int i = 0; i < changes.size(); i++) {
        total += changes[i];
        if(i < window - 1) {
            continue;
        }
        double avg = total / window;
        total -= changes[i - window + 1];
        smooth.push_back(avg);

    }
    // Create running avg vector 
    std::vector<double> runningAvg;
    total = 0;
    double count = 0;
    double avg;
    for(int i = 0; i < smooth.size(); i++) {
        count += 1;
        total += smooth[i];
        avg = total / count;
        runningAvg.push_back(avg);
    }
 
    // Create running stdev vector 
    std::vector<double> deviations;
    total = 0;
    count = 0;
    double diff;
    for(int i = 0; i < smooth.size(); i++) {
        diff = 0;
        total += smooth[i];
        count += 1;
        avg = total / count;
        for(int a = 0; a <= i; a++) {
            diff += pow(smooth[a] - avg, 2);
        }
        double variance = diff / count;
        double stdev = sqrt(variance);
        deviations.push_back(stdev);
    }
    // Normalize values
    std::vector<double> normalValues;
    for(int i = 0; i < smooth.size(); i++) {
        double normalVal = (smooth[i] - runningAvg[i]) / deviations[i];
        normalValues.push_back(normalVal);
    }
 
    return normalValues;
}

std::vector<double> unpack(std::string path) {
    // pull single column of price data from csv
    std::vector<double> out;
    std::ifstream input(path);
    std::string str;
    while(getline(input, str)) {
        out.push_back(std::stod(str));
    }
    return out;
}
std::vector<double> profit(std::vector<double> bids, std::vector<double> asks, double stdThreshold, double profitThreshold, double window) {
    //Loop over dataset and return the profit AND number of transactions (to display later)
    std::vector<double> out;
    double xmr = 3;
    double usd = 0;
    bool holding = true;
    double price;
    double entry = bids[0];
    double transactions = 0;
    std::vector<double> normal = go(asks, window);
    for(int i = 0; i < normal.size(); i++) {
        if (normal[i] <= -stdThreshold && not holding ) {
            //buy
            transactions += 1;
                price = bids[i];
                // std::cout << "buying at " << price << std::endl;
                
                xmr = (usd / price) * (1- .0026); //<-- fee
                usd = 0;
                holding = true;
                entry = price;
                continue;
            
        }
        if (holding) { 
            price = asks[i];
            if (price >= profitThreshold * entry | normal[i] >= stdThreshold) {
            //sell
            transactions += 1;
            usd = (xmr * price) * (1 - .0026);
            xmr = 0;
            holding = false;
            continue;
            }
        }
    }
    if(holding) {
        out.push_back( xmr / 3 - 1);
    }
    else {
        out.push_back(usd / (bids[0] * 3) - 1);
    }
    out.push_back(transactions);
    return out;
}

//create combos to be tested
std::vector<std::vector<double>> combos() {
    std::vector<std::vector<double>> out;
    for(double i = 1.5; i <= 4.1; i += 0.1) {
        for(double a = 1.005; a <= 1.03; a += 0.001) {
            for(double c = 30; c <= 240; c += 15) {
                std::vector<double> combo = {i, a, c};
                out.push_back(combo);
            }
        }
    }
    return out;
}
// to help visualize results
void printCombo(std::vector<double> combo) {
    std::cout << '(';
    for(int i = 0; i < combo.size(); i++) {
        if(i == 2) {
            std::cout << combo[i];
        }
        else {
            std::cout << combo[i] << " ";
        }
        
    }
    std::cout << ") ";
}

void write(std::vector<std::vector<double>> data)  {
	// take vectors (columns) and write to csv
        int colCount = data.size();
        std::ofstream ofs("data.csv");
        for(int i = 0; i < data[0].size(); i++) {
                for(int a = 0; a < colCount; a++) {
                        ofs << data[a][i] << ',';
                }
                ofs << std::endl;
        }
        ofs.close();
}

int main() {
    // unpack data
    std::vector<double> asks = unpack("asks.csv");
    std::vector<double> bids = unpack("bids.csv");
    // baseline - what would the profit be if I just bought and held?
    double holdingProfit = (asks[-1] / asks[0]) - 1;
    // inputs to be tested
    std::vector<std::vector<double>> inputs = combos();
    // csv output
    std::ofstream ofs("result.csv");
    ofs << "stdThresh," << "profitThresh," << "window," << "profit," << "txcount," << std::endl;
    for(int i = 0; i < inputs.size(); i++) {
        ofs << inputs[i][0] << ',' << inputs[i][1] << ',' << inputs[i][2] << ',';
	std::vector<double> result = profit(bids, asks, inputs[i][0], inputs[i][1], inputs[i][2]);
	ofs << result[0] << ',' << result[1] << ',' << std::endl;
    }
    return 0;
}
