%% Load in data
load("C:\Users\afari\Downloads\a.mat");


%% Convert data
time = collected_data.time_internal_seconds;
torque = collected_data.force_dyno_lbs * 8/12;
engine_rpm = double(collected_data.dyno_engine_speed);
secondary_rpm = double(collected_data.dyno_secondary_speed);


%% Plot data without bounds
figure;
hold on;
title("Dyno Test 3");
subplot(3,2,1);
plot(time, engine_rpm);
subplot(3,2,2);
plot(time, engine_rpm./secondary_rpm);
subplot(3,2,3);
plot(time, torque);
subplot(3,2,4)
plot(engine_rpm, torque);
subplot(3,2,5);
plot(engine_rpm./secondary_rpm, torque);


%% Plot data with bounds
time_begin = 0;
time_end = 60;

figure;
hold on;
title("Dyno Test 3");
subplot(3,2,1);
plot(time, engine_rpm);
title("Engine RPM");
xlabel("Time (s)");
ylabel("Engine Speed (RPM)");
xlim([time_begin time_end])
ylim([0 4000]);

subplot(3,2,3);
plot(time, engine_rpm./secondary_rpm);
title("CVT Ratio");
xlabel("Time (s)");
ylabel("CVT Ratio");
xlim([time_begin time_end])
ylim([0 5]);
subplot(3,2,5);
plot(time, torque);
title("Output Torque");
xlabel("Time (s)");
ylabel("Torque (ft-lbs)");
xlim([time_begin time_end])
subplot(3,2,2);
plot(time, secondary_rpm);
title("Secondary RPM");
xlabel("Time (s)");
ylabel("Secondary Speed (RPM)");
xlim([time_begin time_end])
ylim([0 4000]);
subplot(3,2,4)
scatter(engine_rpm, torque, 3);
xlabel("Engine Speed (RPM)");
ylabel("Torque (ft-lbs)");
xlim([0 4000]);
subplot(3,2,6);
scatter(engine_rpm./secondary_rpm, torque, 3);
xlabel("CVT Ratio");
ylabel("Torque (ft-lbs)");
xlim([0 5])

%%
figure;
fs = 100;
y = fft(torque);

n = length(torque);          % number of samples
f = (0:n-1)*(fs/n);     % frequency range
power = abs(y).^2/n;    % power of the DFT


plot(f,power)
xlabel('Frequency')
ylabel('Power')
ylim([0 500])

%%
y0 = fftshift(y);         % shift y values
f0 = (-n/2:n/2-1)*(fs/n); % 0-centered frequency range
power0 = abs(y0).^2/n;    % 0-centered power

figure;
plot(f0,power0)
xlabel('Frequency')
ylabel('Power')
ylim([0 500])

mask = transpose(abs(f0) < 10);
yf = y0 .* mask;
powerf = abs(yf).^2/n;

figure;
plot(f0,powerf);
xlabel('Frequency')
ylabel('Power')
ylim([0 500])


%%
yafter = ifft(yf);
figure;
plot(yafter);
ylim([0 50])
figure;
plot(torque);
ylim([0 50])




















