#ifndef TASKFEMFRICTIONLESS_H
#define TASKFEMFRICTIONLESS_H

#include <QMainWindow>

namespace Ui {
class TaskFemFrictionless;
}

class TaskFemFrictionless : public QMainWindow
{
    Q_OBJECT

public:
    explicit TaskFemFrictionless(QWidget *parent = 0);
    ~TaskFemFrictionless();

private:
    Ui::TaskFemFrictionless *ui;
};

#endif // TASKFEMFRICTIONLESS_H
