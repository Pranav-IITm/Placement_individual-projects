% DISPLACEMENT_ANALYSIS
% Compare electrostatic cantilever displacement for different geometries.
% Uses the same lumped parallel-plate analytical model as parameter_sweep.m.

clear; clc; close all;

eps0 = 8.854e-12;
E = 169e9;
V = linspace(0, 30, 301);

% Each row: [L, w, t, gap] in micrometres.
devices = [
    150, 20, 2.0, 4.0;
    200, 20, 2.0, 4.0;
    250, 20, 2.0, 4.0;
    200, 20, 1.5, 4.0;
];

figure('Name','Displacement comparison');
hold on;

for n = 1:size(devices,1)
    p.L = devices(n,1)*1e-6;
    p.w = devices(n,2)*1e-6;
    p.t = devices(n,3)*1e-6;
    p.g = devices(n,4)*1e-6;
    p.E = E;
    p.eps0 = eps0;

    I = p.w*p.t^3/12;
    k = 3*p.E*I/p.L^3;
    A = p.L*p.w;
    Vpi = sqrt(8*k*p.g^3/(27*p.eps0*A));

    x = nan(size(V));
    for j = 1:numel(V)
        if V(j) < Vpi
            equilibrium = @(defl) k*defl - p.eps0*A*V(j)^2/(2*(p.g-defl)^2);
            x(j) = fzero(equilibrium, [0, p.g/3]);
        end
    end

    plot(V, x*1e6, 'LineWidth', 1.4, ...
        'DisplayName', sprintf('L=%gum, t=%gum, V_{PI}=%.1fV', ...
        devices(n,1), devices(n,3), Vpi));
end

xlabel('Actuation voltage [V]');
ylabel('Tip displacement [um]');
title('Electrostatic MEMS cantilever displacement');
legend('Location','northwest');
grid on;
hold off;

% Note: points at/above the estimated pull-in voltage are intentionally
% left undefined because the simple static model does not describe the
% post-pull-in dynamics or contact regime.
