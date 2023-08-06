# Program for calibrating openseespy uniaxial materials
# Version: 0.9
# Date: March 2023

import matplotlib.pyplot as plt
import numpy as np
import openseespy.opensees as ops
import os
import re
import random
from datetime import datetime
import numbers
import webbrowser

class unimatcalibrate:
    def __init__(self, name, matcommand, variables, file_strain, file_stress, gainstances, num_Runs=5,
                 previousPop=True):
        self.Name = name
        self.matCommand = matcommand
        self.File_Strains = file_strain
        self.File_Stresses = file_stress
        self.Variables = variables
        self.GAInstance = gainstances
        self.Num_Runs = num_Runs
        self.PrePop = previousPop

    def __get_gainstances(self):
        return self._GAInstance

    def __set_gainstances(self, value):
        if not isinstance(value, list):
            value = [value]

        self._GAInstance = value

    def __del_gainstances(self):
        del self._GAInstance

    GAInstance = property(__get_gainstances, __set_gainstances, __del_gainstances)

    def __mst(self, Y):
        Y = np.array(Y)
        avg = np.mean(Y)
        m = len(Y)
        mst_ = np.sum((Y - avg) ** 2) / m
        return mst_

    def __mse(self, X, Y):
        Y = np.array(Y)
        X = np.array(X)
        m = len(Y)
        mse_ = np.sum((X - Y) ** 2) / m
        rmse_ = np.sqrt(mse_)
        return mse_, rmse_

    def __r_sequard(self, X, Y):
        return 1 - (self.__mse(X, Y)[0] / self.__mst(Y))

    def __mae(self, X, Y):
        Y = np.array(Y)
        X = np.array(X)
        m = len(Y)
        mae_ = np.sum(np.abs(X - Y)) / m
        return mae_

    def __mape(self, X, Y):
        Y = np.array(Y)
        X = np.array(X)
        m = len(Y)
        mape_ = np.sum(np.abs((X - Y) / Y)) / m
        return mape_

    def __smape(self, X, Y):
        Y = np.array(Y)
        X = np.array(X)
        m = len(Y)
        smape_ = np.sum(np.abs((X - Y) / ((np.abs(X) + np.abs(Y)) / 2))) / m
        return smape_

    def run(self, error='r_2', fun_solution=None, gene_change_per=20, gene_change=[], file_save_solution='solution.txt',
            file_save_stress='strain_stress.txt'):
        """
        Function to perform optimization(find best fit)

        error: String, error type used to calculate error. Valid values for this argument are 'r_2', 'mse', 'rmse',
               'mae', 'mape', 'smape' ( Default value is 'r_2').

        fun_solution: Python function, program calculates final solution from solutions obtained from each individual
               run using this function. If fun_solution=None, the solution with maximum fitness will be selected as the
                best solution.(Default value is None).

        gene_change_per: float, Variable range will be changed gene_change_per percent at current run according to the
              solution obtained from the previous run(If the fitness is changed).To prevent the program from changing
              the variable ranges, set gene_change_per value to 0 (optional default is 20).

              Example:
              Var = [a, b]
              solution = c
              New var = [a + (c - a) * p, b - (b - c) * p]

              Note:
              This will be applied to the selected variables in gene_change argument.
              if you set gene_change to an empty list (Default value) it will be applied to all variables.

        gene_change: Python list, The names of the variables whose range is changed. (Default value is [])

        file_save_solution: String, The name of the file where the final solution is saved.

        file_save_stress: String, The name of the file where the calculated stresses/forces and strains/displacements
               are saved.

        return: solution_final, allsolutions, allfitnesses
                solution_final: Python list, final solution ( calculated using fun_solution or the one with maximum fitness)
                allsolutions: Python list, a list contains the best solutions obtained from each run.
                allfitnesses: Python list, a list contains the best fitnesses obtained from each run.
        """

        if error.lower() not in ['r_2', 'mse', 'rmse', 'mae', 'mape', 'smape']:
            raise ValueError('error must be one of \'r_2\', \'mse\', \'rmse\', \'mae\', \'mape\' or \'smape\'')

        if not isinstance(gene_change_per, numbers.Number):
            raise ValueError('gene_change_per must be a numeric value')

        error = error.lower()

        try:
            start_time = datetime.now().replace(microsecond=0)
            if self.Num_Runs <= 0:
                self.Num_Runs = 1
                print('Num_Run was set to 1')
            if type(self.Num_Runs) == float:
                self.Num_Runs = int(self.Num_Runs)
                print('Num_Run was set to ', self.Num_Runs)

            if self.Num_Runs > len(self.GAInstance):
                gains = self.GAInstance
                gains_f = gains[-1]
                dif = self.Num_Runs - len(gains)
                for i in range(dif):
                    gains.append(gains_f)

                self.GAInstance = gains

            strain, stress = self.__getstrainstress()
            if error in ['mape', 'smape']:
                a = True
                while a:
                    if strain[0] == 0.0 and stress[0] == 0.0:
                        a = True
                    else:
                        break
                    stress.pop(0)
                    strain.pop(0)

            global gennumber
            global perrun
            global errors
            global fitnesses
            global x_plot
            global y_plot
            gennumber = 0
            perrun = 0
            errors = []
            fitnesses = []
            fig1 = plt.figure(dpi=200)
            ax1 = plt.axes()
            x_plot = []
            y_plot = []
            def fitness_func(solution, solution_idx):
                global gennumber
                global perrun
                global x_plot
                global y_plot
                global errors

                perrun_ = round(100 * gennumber / self.GAInstance[0].num_generations / self.GAInstance[0].sol_per_pop / self.Num_Runs, 1)
                if perrun < perrun_:
                    perrun = perrun_
                    max_index = fitnesses.index(max(fitnesses))
                    err_cur = errors[max_index]

                    err_label = error.upper()
                    err_best = '0'
                    err_worst = '+inf'
                    if error == 'r_2':
                        err_best = '1.0'
                        err_worst = '-inf'
                        err_label = 'R\u00b2'

                    if error == 'smape':
                        err_worst = '2.0'


                    err_mas = err_label + ':  ' + str(round(err_cur, 4))
                    if perrun < 100:
                        print(str(perrun) + ' %' + '    ' + err_mas + '   best value: ' + err_best +
                              '   worst value: ' + err_worst + '    Model: ' + self.Name)
                        x_plot.append(perrun)
                        y_plot.append(err_cur)

                gennumber += 1
                stress_ = self.__calcstress(solution, strain)
                mst_ = 1
                if error == 'r_2':
                    mst_ = self.__mst(stress)

                if error == 'mse':
                    s, rs = self.__mse(stress_, stress)
                    if np.isnan(s):
                        fitness = 1e-15
                    else:
                        fitness = 1 / (s + 0.000001)
                elif error == 'rmse':
                    rs, s = self.__mse(stress_, stress)
                    if np.isnan(s):
                        fitness = 1e-15
                    else:
                        fitness = 1 / (s + 0.000001)
                elif error == 'r_2':
                    s = 1 - (self.__mse(stress_, stress)[0] / mst_)
                    if np.isnan(s):
                        fitness = -1e15
                    else:
                        fitness = s
                elif error == 'mae':
                    s = self.__mae(stress_, stress)
                    if np.isnan(s):
                        fitness = 1e-15
                    else:
                        fitness = 1 / (s + 0.000001)
                elif error == 'mape':
                    s = self.__mape(stress_, stress)
                    if np.isnan(s):
                        fitness = 1e-15
                    else:
                        fitness = 1 / (s + 0.000001)

                elif error == 'smape':
                    s = self.__smape(stress_, stress)
                    if np.isnan(s):
                        fitness = 1e-15
                    else:
                        fitness = 1 / (s + 0.000001)

                errors.append(s)
                fitnesses.append(fitness)
                return fitness

            allsolutions = []
            allfitnesses = []
            new_variables = {}
            best_fit = 1e-15
            solution_fitness_ = 1e-15
            change_var = False
            for j in range(self.Num_Runs):
                print('Run : ' + str(j + 1))
                ga_instance = self.GAInstance[j]
                ga_instance.fitness_func = fitness_func

                if j > 0:
                    if change_var:
                        if gene_change_per > 0:
                            self.Variables = new_variables
                            new_gen_space = gen_space(new_variables)
                            ga_instance.gene_space = new_gen_space
                            print('gen_space was changed')

                ga_instance.run()

                if self.PrePop:
                    inipop = ga_instance.population
                    ga_instance.initial_population = inipop

                solution_, solution_fitness_, solution_idx_ = ga_instance.best_solution()

                if round(best_fit, 4) < round(solution_fitness_, 4):
                    change_var = True
                    best_fit = solution_fitness_
                else:
                    change_var = False

                allsolutions.append(solution_)
                allfitnesses.append(solution_fitness_)
                if gene_change_per > 0:
                    if change_var:
                        new_variables = self.__change_var_range(solution_, gene_change_per, gene_change)

            if self.Num_Runs == 1:
                solution_final = solution_
            else:
                if fun_solution == None:
                   bindex = np.argmax(allfitnesses)
                   solution_final = allsolutions[bindex]
                else:
                   solution_final = fun_solution(allsolutions)

            print('100.0 %')
            self.__printsolution(solution_final)
            self.__savesolution(file_save_solution, file_save_stress, solution_final, strain)

            end_time = datetime.now().replace(microsecond=0)
            print('Start Time: {}'.format(start_time))
            print('End Time: {}'.format(end_time))
            print('Duration: {}'.format(end_time - start_time))

            if len(x_plot) > 1:
                ax1.plot(x_plot, y_plot, linewidth=2.0, color='deepskyblue')

            err_best = 0
            err_label = error.upper()
            if error == 'r_2':
                err_best = 1
                err_label = 'R\u00b2'

            ax1.plot([0, 100], [err_best, err_best], '--', linewidth=2.0, color='lightseagreen')
            ax1.legend([err_label, 'Best ' + err_label])
            ax1.set_title('Convergence Curve[' + self.Name + ']    ' + err_label + ' = ' + str(round(y_plot[-1], 4)))
            ax1.set_xlim([0, 100])
            ax1.set_xlabel('Step[%]')
            ax1.set_ylabel(err_label)
            ax1.grid(True)

            self.plotsolution(solution_final)

            return solution_final, allsolutions, allfitnesses

        except OverflowError:
            print('Overflow Error')
            exit()
    def plotsolution(self, solution):
        strain, stress = self.__getstrainstress()
        stress_ = self.__calcstress(solution, strain)

        fig1 = plt.figure(dpi=200)
        ax1 = plt.axes()
        ax1.plot(strain, stress, linewidth=1, linestyle="--", color='r')
        ax1.plot(strain, stress_, linewidth=1, color='b')
        ax1.set_xlabel("Strain / Displacement")
        ax1.set_ylabel("Stress / Force")
        ax1.legend(['Experimental', 'Calibrated'])
        ax1.set_title(self.Name)
        ax1.grid(True)

        fig2 = plt.figure(dpi=200)
        ax2 = plt.axes()
        ax2.plot(range(len(stress)), stress, linewidth=1, linestyle="--", color='r')
        ax2.plot(range(len(stress_)), stress_, linewidth=1, color='b')
        ax2.set_xlabel("Step")
        ax2.set_ylabel("Stress / Force")
        ax2.legend(['Experimental', 'Calibrated'])
        ax2.set_title(self.Name)
        ax2.grid(True)
        plt.show()

    ##  Stress And Strain
    def __getstrainstress(self):
        file_strain, file_stress = self.File_Strains, self.File_Stresses
        strain = []
        stress = []
        with open(file_strain) as f:
            lines = f.readlines()
        for line in lines:
            line2 = line.split(" ")
            strain.append(float(line2[0]))
        f.close()

        with open(file_stress) as f:
            lines = f.readlines()
        for line in lines:
            line2 = line.split(" ")
            stress.append(float(line2[0]))
        f.close()

        return strain, stress

    def __getStress(self,matcommand_, strain_):
        logfilename = 'opslogfile.txt'
        ops.logFile(logfilename, '-noEcho')
        ops.wipe()
        if isinstance(matcommand_, list):
            for mat_comm in matcommand_:
                eval(mat_comm)
        else:
            eval(matcommand_)
        ops.testUniaxialMaterial(1)
        stress = []
        for eps in strain_:
            ops.setStrain(eps)
            stress.append(ops.getStress())

        return stress

    ## Calculate Stresses
    def __calcstress(self, solution_, strain_):
        if isinstance(self.matCommand, list):
            mat_commands = []
            num_mats = len(self.matCommand)
            st_vars = 0
            for i in range(num_mats):
                mat_vars = self.Variables[i]
                num_vars = len(mat_vars.keys())
                mat_comm = self.matCommand[i]
                mat_comm = 'ops.' + mat_comm
                mat_sol = solution_[st_vars: st_vars + num_vars]
                for j in range(len(mat_sol)):
                    mat_comm = re.sub(r"\b%s\b" % list(mat_vars.keys())[j], str(mat_sol[j]), mat_comm)
                mat_commands.append(mat_comm)
                st_vars += num_vars

            stress_ = self.__getStress(mat_commands, strain_)
        else:
            matcommand_ = 'ops.' + self.matCommand
            for i in range(len(solution_)):
                matcommand_ = re.sub(r"\b%s\b" % list(self.Variables.keys())[i], str(solution_[i]), matcommand_)

            stress_ = self.__getStress(matcommand_, strain_)
        return stress_

    def __change_var_range(self, solution, ch_per, gene_change):
        p = ch_per / 100
        if isinstance(self.Variables, list):
            num_mats = len(self.matCommand)
            var_new = []
            st_vars = 0
            for i in range(num_mats):
                mat_vars = self.Variables[i]
                mat_keys = list(mat_vars.keys())
                if len(gene_change) == 0:
                    ch_vars = mat_keys
                else:
                    ch_vars = gene_change[i]

                num_vars = len(mat_vars.keys())
                mat_sol = solution[st_vars: st_vars + num_vars]
                for j in range(num_vars):
                    if mat_keys[j] in ch_vars:
                        if len(list(mat_vars.values())[j]) == 1:
                            continue

                        c = mat_sol[j]
                        a, b = list(mat_vars.values())[j][0], list(mat_vars.values())[j][1]
                        a_ = a + (c - a) * p
                        b_ = b - (b - c) * p
                        mat_vars[mat_keys[j]][0] = a_
                        mat_vars[mat_keys[j]][1] = b_
                st_vars += num_vars
                var_new.append(mat_vars)
        else:
            var_new = self.Variables
            mat_keys = list(var_new.keys())
            if len(gene_change) == 0:
                ch_vars = mat_keys
            else:
                ch_vars = gene_change

            for i in range(len(solution)):
                if mat_keys[i] in ch_vars:
                    if len(list(self.Variables.values())[i]) == 1:
                        continue

                    c = solution[i]
                    a, b = list(self.Variables.values())[i][0], list(self.Variables.values())[i][1]
                    a_ = a + (c - a) * p
                    b_ = b - (b - c) * p
                    var_new[mat_keys[i]][0] = a_
                    var_new[mat_keys[i]][1] = b_

        return var_new

    def __printsolution(self, solution_final):
        print('Final Solusion: ')
        if isinstance(self.Variables, list):
            mat_commands = []
            num_mats = len(self.matCommand)
            st_vars = 0
            for i in range(num_mats):
                mat_vars = self.Variables[i]
                num_vars = len(mat_vars.keys())
                mat_comm = self.matCommand[i]
                mat_comm = 'ops.' + mat_comm
                mat_sol = solution_final[st_vars: st_vars + num_vars]
                print('# Material ' + str(i + 1) + ':' + '\n')
                for j in range(len(mat_sol)):
                    print(str(list(mat_vars.keys())[j]) + ' = ' + str(mat_sol[j]) + '\n')
                print(mat_comm + '\n')
                st_vars += num_vars

        else:
            for i in range(len(solution_final)):
                print(str(list(self.Variables.keys())[i]) + ' = ' + str(solution_final[i]) + '\n')
            print(self.matCommand + '\n')

    def __savesolution(self, file_save_solution, file_save_stress, solution_final, strain_):
        if file_save_solution != '':
            if os.path.exists(file_save_solution):
                os.remove(file_save_solution)

            f = open(file_save_solution, "w")

            if isinstance(self.Variables, list):
                num_mats = len(self.matCommand)
                st_vars = 0
                for i in range(num_mats):
                    mat_vars = self.Variables[i]
                    num_vars = len(mat_vars.keys())
                    mat_comm = self.matCommand[i]
                    mat_comm = 'ops.' + mat_comm
                    mat_sol = solution_final[st_vars: st_vars + num_vars]
                    f.write('# Material ' + str(i + 1) + ':' + '\n')

                    for j in range(len(mat_sol)):
                        f.write(str(list(mat_vars.keys())[j]) + ' = ' + str(mat_sol[j]) + '\n')
                    st_vars += num_vars
                    f.write(mat_comm + '\n')
                    f.write('\n')

            else:
                for i in range(len(solution_final)):
                    f.write(str(list(self.Variables.keys())[i]) + ' = ' + str(solution_final[i]) + '\n')
                mat_comm = self.matCommand
                mat_comm = 'ops.' + mat_comm
                k = f.write(mat_comm + '\n')

            f.close()

        if file_save_stress != '':
            stress_ = self.__calcstress(solution_final, strain_)
            if os.path.exists(file_save_stress):
              os.remove(file_save_stress)

            f = open(file_save_stress, "w")
            for i in range(len(strain_)):
                k = f.write(str(strain_[i]) + ' , ' + str(stress_[i]) + '\n')

            f.close()

    def __gen_space(self, variables):
        gene_space_ = []
        if isinstance(variables, list):
            for vars in variables:
                for vals in vars.values():
                    if len(vals) == 1:
                        gene_space_.append(vals)
                    elif len(vals) == 2:
                        gene_space_.append({'low': vals[0], 'high': vals[1]})
                    elif len(vals) == 3:
                        gene_space_.append(np.arange(vals[0], vals[1] + vals[2], vals[2]))
        else:
            for vals in variables.values():
                if len(vals) == 1:
                    gene_space_.append(vals)
                elif len(vals) == 2:
                    gene_space_.append({'low': vals[0], 'high': vals[1]})
                elif len(vals) == 3:
                    gene_space_.append(np.arange(vals[0], vals[1] + vals[2], vals[2]))

        return gene_space_

def uniMatTester(ops,name, matTag, strain, stress=[],  error='r_2'):
    """
    Function to calculate stresses/forces of given strains/displacements using testUniaxialMaterial function of
    openseespy.opensees object.

    ops: openseespy.opensees object
    name: String, the name of the project(model).
    matTag: Integer, Tag of the uniaxial material.
    strain: Python list, a list of strains/displacements
    stress: Python list, a list of stresses/forces (optional, default value is an empty list). If stress = []
           experimental stress/force curve won't be plotted.
    error: String, error type used to calculate error. Valid values for this argument are 'r_2', 'mse', 'rmse',
            'mae', 'mape', 'smape' ( Default value is 'r_2').
    return: Python list, calculated stresses/forces

    Example:
    import opsmatcal.matcalibrate as omc
    import openseespy.opensees as ops

    disp = [0, 1, 2, 3, 4]
    force = [0, 1000, 2000, 3000, 4000]
    Fy = 460.0
    E0 = 2E5
    b = 0.02
    cR1 = 0.8
    cR2 = 0.05
    matTag = 1
    ops.uniaxialMaterial('Steel02', matTag, Fy, E0, b, 18, cR1, cR2)
    _forces = omc.uniMatTester(ops,'mymodel', matTag, strain=disp, stress=force,  error='r_2')
    """

    if error.lower() not in ['r_2', 'mse', 'rmse', 'mae', 'mape', 'smape']:
        raise ValueError('error must be one of \'r_2\', \'mse\', \'rmse\', \'mae\', \'mape\' or \'smape\'')

    error = error.lower()

    logfilename = 'opslogfile.txt'
    ops.logFile(logfilename, '-noEcho')
    # ops.wipe()

    ops.testUniaxialMaterial(matTag)
    if error in ['mape', 'smape']:
        a = True
        while a:
            if strain[0] == 0.0 and stress[0] == 0.0:
                a = True
            else:
                break
            stress.pop(0)
            strain.pop(0)

    stress_ = []
    for eps in strain:
        ops.setStrain(eps)
        stress_.append(ops.getStress())

    fig2 = plt.figure(dpi=200)
    ax2 = plt.axes()
    if len(stress) != 0:
        err_label = error.upper()
        err_best = '0'
        err_worst = '+inf'
        if error == 'r_2':
            err_best = '1.0'
            err_worst = '-inf'
            err_label = 'R\u00b2'

        if error == 'smape':
            err_worst = '2.0'

        Y = np.array(stress)
        X = np.array(stress_)
        m = len(Y)
        if error == 'mse':
            err_val = np.sum((X - Y) ** 2) / m
        if error == 'rmse':
            mse_ = np.sum((X - Y) ** 2) / m
            err_val = np.sqrt(mse_)
        if error == 'r_2':
            avg = np.mean(Y)
            mst_ = np.sum((Y - avg) ** 2) / m
            mse_ = np.sum((X - Y) ** 2) / m
            err_val = 1 - (mse_ / mst_)
        if error == 'mae':
            err_val = np.sum(np.abs(X - Y)) / m
        if error == 'mape':
            err_val = np.sum(np.abs((X - Y) / Y)) / m
        if error == 'smape':
            err_val = np.sum(np.abs((X - Y) / ((np.abs(X) + np.abs(Y)) / 2))) / m

        err_mas = err_label + ':  ' + str(round(err_val, 4))
        print(err_mas + '   best value: ' + err_best + '   worst value: ' + err_worst)

        ax2.plot(range(len(stress)), stress, linewidth=1, linestyle="--", color='r')
    ax2.plot(range(len(stress_)), stress_, linewidth=1, color='b')
    ax2.set_xlabel("Step")
    ax2.set_ylabel("Stress / Force")
    if len(stress) != 0:
        ax2.legend(['Experimental', 'Calibrated'])

    ax2.grid(True)
    ax2.set_title(name)

    fig1 = plt.figure(dpi=200)
    ax1 = plt.axes()
    if len(stress) != 0:
         ax1.plot(strain, stress, linewidth=1, linestyle="--", color='r')
    ax1.plot(strain, stress_, linewidth=1, color='b')
    ax1.set_xlabel("Strain / Displacement")
    ax1.set_ylabel("Stress / Force")
    if len(stress) != 0:
        ax1.legend(['Experimental', 'Calibrated'])
    ax1.grid(True)
    ax1.set_title(name)
    plt.show()

    return stress_, err_val

def fitness_func(solution, solution_idx):
    pass

def initial_population(num_poulation, variables):
    inipop = []
    for k in range(num_poulation):
        pop_ = []
        if isinstance(variables, list):
            for vars in variables:
                for vals in vars.values():
                    pop_.append(random.random() * (vals[1] - vals[0]) + vals[0])
        else:
            for vals in variables.values():
                pop_.append(random.random() * (vals[1] - vals[0]) + vals[0])
        inipop.append(pop_)

    return inipop

def gen_space(variables):
    gene_space_ = []
    if isinstance(variables, list):
        for vars in variables:
            for vals in vars.values():
                if len(vals) == 1:
                    gene_space_.append(vals)
                if len(vals) == 2:
                     gene_space_.append({'low': vals[0], 'high': vals[1]})
                elif len(vals) == 3:
                    gene_space_.append(np.arange(vals[0], vals[1] + vals[2], vals[2]))

    else:
        for vals in variables.values():
            if len(vals) == 1:
                gene_space_.append(vals)
            if len(vals) == 2:
                gene_space_.append({'low': vals[0], 'high': vals[1]})
            elif len(vals) == 3:
                gene_space_.append(np.arange(vals[0], vals[1] + vals[2], vals[2]))

    return gene_space_

def getDoc():
    webbrowser.open('https://drive.google.com/file/d/1qUoTewxzERZKUqCiSyMkAUqFCrTL1BQK/view?usp=sharing')
