% PARAMETER_SWEEP
% Basic parameter study for an electrostatically actuated MEMS cantilever.
% This is an analytical/parameter-study model, not a finite-element solver.

clear; clc; close all;

%% Physical constants
params.eps0 = 8.854e-12;      % Vacuum permittivity [F/m]
params.E    = 169e9;          % Young's modulus, silicon [Pa]

%% Nominal cantilever geometry
params.L = 200e-6;             % Length [m]
params.w = 20e-6;              % Width [m]
params.t = 2e-6;               % Thickness [m]
params.g = 4e-6;               % Initial electrode gap [m]

%% Actuation voltage
V = linspace(0, 30, 301);      % Voltage sweep [V]

%% Nominal voltage-displacement curve
[x, Veff, Vpi] = cantilever_response(V, params);

figure('Name','Nominal voltage sweep');
plot(Veff, x*1e6, 'LineWidth', 1.5);
xlabel('Actuation voltage [V]');
ylabel('Tip displacement [um]');
title(sprintf('Electrostatic cantilever: estimated pull-in = %.2f V', Vpi));
grid on;

%% Geometry parameter sweep
L_values = [100 150 200 250 300] * 1e-6;
t_values = [1 1.5 2 2.5 3] * 1e-6;

% Pull-in voltage estimate for a parallel-plate lumped model:
% V_pi = sqrt(8*k*g^3/(27*epsilon0*A)),
% where k = E*w*t^3/(4*L^3) for the first-mode-equivalent tip stiffness.
Vpi_L = zeros(size(L_values));
for i = 1:numel(L_values)
    p = params;
    p.L = L_values(i);
    Vpi_L(i) = pull_in_voltage(p);
end

Vpi_t = zeros(size(t_values));
for i = 1:numel(t_values)
    p = params;
    p.t = t_values(i);
    Vpi_t(i) = pull_in_voltage(p);
end

figure('Name','Geometry parameter sweep');
tiledlayout(1,2);
nexttile;
plot(L_values*1e6, Vpi_L, 'o-', 'LineWidth', 1.5);
xlabel('Cantilever length [um]');
ylabel('Estimated pull-in voltage [V]');
title('Length sweep');
grid on;

nexttile;
plot(t_values*1e6, Vpi_t, 'o-', 'LineWidth', 1.5);
xlabel('Cantilever thickness [um]');
ylabel('Estimated pull-in voltage [V]');
title('Thickness sweep');
grid on;

%% Local functions
function [x, Veff, Vpi] = cantilever_response(V, p)
    k = cantilever_stiffness(p);
    A = p.L * p.w;
    Vpi = sqrt(8*k*p.g^3/(27*p.eps0*A));

    % Static equilibrium of the lumped parallel-plate model:
    % k*x = eps0*A*V^2/[2*(g-x)^2].
    % The cubic is solved for each voltage; the stable low-displacement
    % branch is selected while x < g/3. Beyond pull-in, the response is
    % marked unavailable rather than extrapolated.
    x = nan(size(V));
    Veff = V;
    for j = 1:numel(V)
        if V(j) >= Vpi
            continue;
        end
        f = @(defl) k*defl - p.eps0*A*V(j)^2/(2*(p.g-defl)^2);
        x(j) = fzero(f, [0, p.g/3]);
    end
end

function k = cantilever_stiffness(p)
    % Euler-Bernoulli cantilever tip stiffness: k = 3EI/L^3.
    I = p.w*p.t^3/12;
    k = 3*p.E*I/p.L^3;
end

function Vpi = pull_in_voltage(p)
    k = cantilever_stiffness(p);
    A = p.L*p.w;
    Vpi = sqrt(8*k*p.g^3/(27*p.eps0*A));
end
